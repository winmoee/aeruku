import json
import re
import html
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from composio_openai import ComposioToolSet
from datetime import datetime
import dotenv

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("lead_search")


# Apollo Action IDs
APOLLO_PERSON_ENRICH_ACTION_ID = "APOLLO_PEOPLE_ENRICHMENT"
APOLLO_CREATE_CONTACT_ACTION_ID = "APOLLO_CREATE_CONTACT"
APOLLO_UPDATE_CONTACT_ACTION_ID = "APOLLO_UPDATE_CONTACT"
APOLLO_SEARCH_CONTACTS_ACTION_ID = "APOLLO_SEARCH_CONTACTS"
APOLLO_SEARCH_ORGANIZATIONS_ACTION_ID = "APOLLO_ORGANIZATION_SEARCH"
APOLLO_SEARCH_PEOPLE_ACTION_ID = "APOLLO_PEOPLE_SEARCH"
APOLLO_ENRICH_COMPANY_ACTION_ID = "APOLLO_ORGANIZATION_ENRICHMENT"


system_prompt = f"""
你是一个名为 Apollo CRM Assistant 的 AI 助手。你的核心任务是精确、高效地执行用户的指令，利用提供的工具与 Apollo CRM 系统交互以及进行网页信息爬取。

**核心规则:**
1.  **强制工具调用**: 如果用户的请求与下面列出的任何工具的功能相匹配，你 **必须** 调用相应的工具来完成任务。**严禁**在有适用工具的情况下，自行编造答案或跳过工具调用。
2.  **参数提取与使用**: 必须仔细分析用户请求的**每一个细节**，提取所有相关的约束条件（如关键词、**行业/类型**、地点、规模、职位、状态等），并将它们准确映射到**最合适**的工具输入参数。例如，用户提到的行业（"科技公司"）应映射到 `q_organization_keyword_tags` 或类似的相关参数。**切勿忽略用户请求中的任何部分**。
3.  **结果展示**:
    * 除非另有说明或用户指定，所有搜索类工具返回的数据，默认请求 `per_page=10`。
    * 当查询内容是多个数据时，（多个人或者多个公司）**必须** 使用 **表格** 格式清晰展示结果。
    * 对于返回结果包含多个相关列表的工具（见各工具的"特别注意"部分），你 **必须** 尝试合并主要相关列表中的数据（例如，合并 `organizations` 和 `accounts` 列表），目标是在展示的表格中达到 `per_page` 的数量（默认 15 条）。
4.  **分页提示**: 对于搜索类工具，如果结果分页，**必须** 告知用户 API 返回的总共有多少条数据，共多少页（此总数基于 API 内部的所有匹配项），并提示用户可以查看下一页或指定页码。
5.  **信息准确性**: **严禁**编造任何数据，尤其是联系方式、公司详情等。所有信息必须来自工具的返回结果。
6.  **积分与权限**: 注意提醒用户某些操作（如搜索、丰富）会消耗 Apollo 积分，某些操作（如更新、丰富）需要主 API 密钥权限。
7.  **解释说明**: 当用户询问某个工具或操作如何使用时，**必须** 详细解释其功能、参数和用法。

**可用工具:**

---

### 1️⃣ **搜索联系人 (Search Contacts)** - `{APOLLO_SEARCH_CONTACTS_ACTION_ID}`
* **何时使用**: 当用户要求在你的 Apollo 账户中根据姓名、职位、公司、邮箱或阶段 ID 查找联系人时，**必须** 使用此工具。
* **注意**: 此功能不适用于免费计划用户。限制 50,000 条记录（每页最多 100 条，最多 500 页）。
* **输入参数**:
    * `q_keywords`: (可选) 姓名、职位、公司或邮箱关键词。
    * `contact_stage_ids`: (可选) 联系人阶段 ID 列表。
    * `sort_by_field`: (可选) 排序字段 (例如: `contact_last_activity_date`, `contact_created_at`)。
    * `sort_ascending`: (可选, true/false) 是否升序，需与 `sort_by_field` 配合使用。
    * `per_page`: 每页结果数 (默认遵循核心规则为 10，但此工具最大可设 100)。
    * `page`: 页码。
* **输出**: 联系人搜索结果和分页信息。

---

### 2️⃣ **更新联系人 (Update Contact)** - `{APOLLO_UPDATE_CONTACT_ACTION_ID}`
* **何时使用**: 当用户要求修改 Apollo 系统中**已有**联系人的信息（如姓名、公司、职位、邮箱、标签、阶段等）时，**必须** 使用此工具。
* **注意**: 需要主 API 密钥。
* **输入参数**:
    * `contact_id`: **必填**，要更新的联系人 ID。
    * `first_name`/`last_name`: (可选) 名字/姓氏。
    * `organization_name`: (可选) 公司名称。
    * `title`: (可选) 职位。
    * `email`: (可选) 邮箱。
    * `website_url`: (可选) 公司网站地址。
    * `label_names`: (可选) 标签名称列表 (会覆盖原有标签，请谨慎)。
    * `contact_stage_id`: (可选) 联系人阶段 ID。
    * `account_id`: (可选) 账户 ID。
    * `direct_phone` 等: (可选) 各类电话号码。
* **输出**: 更新后的联系人信息和操作状态。

---

### 3️⃣ **搜索组织 (Search Organizations)** - `{APOLLO_SEARCH_ORGANIZATIONS_ACTION_ID}`
* **何时使用**: 当用户要求根据公司名称、地点、规模、**行业标签/关键词**或 ID 在 Apollo 数据库中查找**公司**时，**必须** 使用此工具。
* **注意**: 搜索消耗积分。限制 50,000 条记录。
* **特别注意**:
    * 务必从用户请求中提取行业、类型等关键词，填入 `q_organization_keyword_tags` 参数。
    * **API 响应主要包含 `organizations` 和 `accounts` 列表。在生成表格时，你 **必须** 合并这两个列表中的公司信息，以优先满足 `per_page` 的数量要求。遵循核心规则 #3 进行展示和沟通。**
* **输入参数**:
    * `q_organization_name`: (可选) 公司名称关键词。
    * `organization_locations`: (可选) 公司总部地点列表。
    * `organization_num_employees_ranges`: (可选) 员工数范围 (例如: "11-50")。
    * `q_organization_keyword_tags`: (可选) **行业关键词或标签 (例如: "technology", "software")**。
    * `organization_ids`: (可选) 特定公司 ID 列表。
    * `organization_not_locations`: (可选) 要排除的地点列表。
    * `per_page`: 每页结果数 (默认遵循核心规则为 10，但此工具最大可设 100)。
    * `page`: 页码。
* **输出**: 公司搜索结果和分页信息。

---

### 4️⃣ **搜索人员 (Search People)** - `{APOLLO_SEARCH_PEOPLE_ACTION_ID}`
* **何时使用**: 当用户要求根据职位、地点、级别、公司域名/ID/地点/规模或关键词在 Apollo 数据库中查找**人员**时，**必须** 使用此工具。
* **注意**: 搜索消耗积分。限制 50,000 条记录。
* **特别注意**:
    * **API 响应主要包含 `people` 和 `contacts` 列表。在生成表格时，你 **必须** 合并这两个列表中的人员信息，以优先满足 `per_page` 的数量要求。遵循核心规则 #3 进行展示和沟通。**
    * 此接口**不**直接返回邮箱/电话。如需获取，请在找到目标人员后，使用"丰富人员信息"工具 (`{APOLLO_PERSON_ENRICH_ACTION_ID}`)。
* **输入参数**:
    * `person_titles`: (可选) 职位列表 (例如: ["Software Engineer", "Product Manager"])。
    * `person_locations`: (可选) 人员地点列表 (例如: ["California, USA"])。
    * `person_seniorities`: (可选) 职位级别列表 (例如: ["manager", "director"])。
    * `organization_locations`: (可选) 公司总部地点列表。
    * `q_organization_domains`: (可选) 公司域名列表。
    * `contact_email_status`: (可选) 邮箱状态 (例如: "verified")。
    * `organization_ids`: (可选) 公司 ID 列表。
    * `organization_num_employees_ranges`: (可选) 公司规模范围。
    * `q_keywords`: (可选) 任意关键词。
    * `per_page`: 每页结果数 (默认遵循核心规则为 10，但此工具最大可设 100)。
    * `page`: 页码。
* **输出**: 人员搜索结果和分页信息。

---

### 5️⃣ **丰富公司信息 (Enrich Company)** - `{APOLLO_ENRICH_COMPANY_ACTION_ID}`
* **何时使用**: 当用户要求获取**特定公司**的详细信息（如行业、营收、员工数、融资情况等），并提供了公司域名时，**必须** 使用此工具。
* **注意**: 需要主 API 密钥。消耗积分。
* **输入参数**:
    * `domain`: **必填**，公司域名 (例如: `example.com`，不要包含 `www.` 或 `@`)。
* **输出**: 指定公司的详细信息。

---

### 6️⃣ **丰富人员信息 (Enrich Person)** - `{APOLLO_PERSON_ENRICH_ACTION_ID}`
* **何时使用**: 当用户要求获取**特定人员**的详细联系方式（如邮箱、电话）或背景信息，并提供了姓名、邮箱、公司、域名、Apollo ID 或 LinkedIn URL 中至少一项时，**必须** 使用此工具。
* **注意**: 需要主 API 密钥。根据请求参数消耗积分。
* **输入参数** (至少提供以下一项):
    * `first_name` / `last_name`: 名字 / 姓氏。
    * `name`: 全名。
    * `email`: 邮箱。
    * `organization_name`: 公司名称。
    * `domain`: 公司域名。
    * `id`: 人员的 Apollo ID。
    * `linkedin_url`: LinkedIn 个人资料 URL。
    * `reveal_personal_emails`: (可选, true/false) 是否尝试获取个人邮箱 (消耗积分)。
    * `reveal_phone_number`: (可选, true/false) 是否尝试获取电话号码 (消耗积分)。
* **输出**: 指定人员的详细联系方式和背景信息。

---

### 7️⃣ **创建联系人 (Create Contact)** - `{APOLLO_CREATE_CONTACT_ACTION_ID}`
* **何时使用**: 当用户明确要求在 Apollo 中创建**新**的联系人，并提供了必要信息时，**必须** 使用此工具。
* **注意**: 需要主 API 密钥。
* **必填参数**:
    * `first_name`: 联系人名字。
    * `last_name`: 联系人姓氏。
* **常用选填参数**:
    * `organization_name`: 公司名称。
    * `website_url`: 公司网站 URL (建议完整格式, 如 `https://www.example.com`)。
    * `title`: 职位。
    * `email`: 邮箱地址。
    * `label_names`: 标签列表 (例如: `["Lead", "Follow Up"]`)。
    * `contact_stage_id`: 联系人阶段 ID。
    * `present_raw_address`: 地址信息。
    * `direct_phone`: 主要电话号码。
* **输出**: 新创建的联系人信息和操作状态。


"""


def _initialize_toolset(composio_api_key: str):
    """Initialize the Composio ToolSet and fetch tool definitions."""
    logger.info("Initializing Composio ToolSet")
    try:
        toolset = ComposioToolSet(api_key=composio_api_key)
        
        actions_to_enable = [
            APOLLO_SEARCH_CONTACTS_ACTION_ID,
            APOLLO_SEARCH_PEOPLE_ACTION_ID,
            APOLLO_SEARCH_ORGANIZATIONS_ACTION_ID,
            APOLLO_ENRICH_COMPANY_ACTION_ID,
            APOLLO_CREATE_CONTACT_ACTION_ID,
            APOLLO_UPDATE_CONTACT_ACTION_ID,
            APOLLO_PERSON_ENRICH_ACTION_ID
        ]
        
        logger.info(f"Fetching tools for {len(actions_to_enable)} actions")
        tools = toolset.get_tools(actions=actions_to_enable)
        
        if not tools:
            logger.error("No tools were returned from Composio")
            raise ValueError("Could not fetch any tool definitions.")
        
        logger.info(f"Successfully fetched {len(tools)} tools")
        if len(tools) != len(actions_to_enable):
            logger.warning(f"Expected {len(actions_to_enable)} tools but got {len(tools)}")
            
        return toolset, tools
        
    except Exception as e:
        logger.error(f"Error initializing Composio ToolSet: {e}", exc_info=True)
        raise RuntimeError(f"Error initializing Composio ToolSet: {e}")

def _clean_text_for_json(text, max_length=2000):
    """Clean and truncate text for JSON encoding"""
    if not text:
        return ""
    original_length = len(text)
    text = text[:max_length] if original_length > max_length else text
    if original_length > max_length:
        logger.debug(f"Truncated text from {original_length} to {max_length} characters")
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = html.unescape(text)
    return text

def _format_tool_result(raw_result) -> str:
    """
    Format tool result into a consistent string representation.
    """
    logger.debug(f"Formatting tool result of type: {type(raw_result)}")
    
    # Handle dictionary or list objects
    if isinstance(raw_result, (dict, list)):
        logger.debug("Formatting dict/list result")
        return json.dumps(raw_result, indent=2, ensure_ascii=False)
    
    # Handle JSON strings
    elif isinstance(raw_result, str) and raw_result.strip().startswith(("{", "[")):
        logger.debug("Attempting to parse and format JSON string")
        try:
            parsed = json.loads(raw_result)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON string, treating as plain text")
            return _clean_text_for_json(raw_result)
    
    # Handle other types
    else:
        logger.debug(f"Converting {type(raw_result)} to string")
        return _clean_text_for_json(str(raw_result))

def _extract_leads_from_tool_result(result_content: str) -> List[Dict[str, Any]]:
    """Extract leads from tool result"""
    logger.info("Extracting leads from tool result")
    leads_list = []
    try:
        # Parse the JSON response
        result_data = json.loads(result_content)
        
        # Extract the people array
        people = result_data.get('data', {}).get('data', {}).get('people', [])
        logger.info(f"Found {len(people)} people in result")
        
        # Process each person as a lead
        for i, person in enumerate(people):
            logger.debug(f"Processing person {i+1}/{len(people)}")
            organization = person.get('organization', {})
            
            lead_record = {
                'first_name': person.get('first_name'),
                'last_name': person.get('last_name'),
                'email': person.get('email'),
                'title': person.get('title'),
                'linkedin_url': person.get('linkedin_url'),
                'city': person.get('city'),
                'state': person.get('state'),
                'country': person.get('country'),
                'company': organization.get('name'),
                'company_website': organization.get('website_url'),
                'phone_number': organization.get('phone'),
                'created_at': datetime.utcnow().isoformat()
            }
            leads_list.append(lead_record)
            
        logger.info(f"Successfully extracted {len(leads_list)} leads")
    except json.JSONDecodeError:
        logger.error("Failed to parse result_content as JSON", exc_info=True)
        print(f"JSON Decode Error. Content: {result_content[:200]}...")
    except Exception as e:
        logger.error(f"Error extracting leads: {str(e)}", exc_info=True)
        print(f"Error extracting leads: {str(e)}")
    
    return leads_list

async def search_leads(
    name: str,
) -> str:
    """
    Search for leads using Apollo CRM integration via LLM and Composio tools.
    """

    query = name['query']

    # Get API keys from parameters or environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    composio_api_key = os.getenv("COMPOSIO_API_KEY")
    
    # Initialize OpenAI client
    client_args = {"api_key": openai_api_key}
    client = OpenAI(**client_args)
    
    # Initialize Composio ToolSet and tools
    toolset, tools = _initialize_toolset(composio_api_key)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content":query}
    ]
    

    logger.info("Adding user message to conversation")
    
    final_content = "Error: Execution failed."
    loop_count = 0
    
    tool_calls_made = []
    tool_results_received = []
    all_leads = []
    
    # Agent loop
    logger.info(f"Starting agent loop")
    print(f"Starting agent loop")
    while loop_count < 1:
        loop_count += 1
        logger.info(f"Starting loop {loop_count}")
        print(f"Starting loop {loop_count}")
        
        try:
            # Call LLM API
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            serializable_message = response_message.model_dump()
            messages.append(serializable_message)
            
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                logger.info("No tool calls in response, ending loop")
                print("No tool calls in response, ending loop")
                final_content = response_message.content
                break
            
            # Track tool calls
            logger.info(f"Processing {len(tool_calls)} tool calls")
            print(f"Processing {len(tool_calls)} tool calls")
            current_tool_calls = []
            for tc in tool_calls:
                tool_call_info = {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                logger.info(f"Tool call: {tc.function.name}")
                print(f"Tool call: {tc.function.name} with args: {tc.function.arguments[:100]}...")
                current_tool_calls.append(tool_call_info)
                tool_calls_made.append(tool_call_info)
            
            # Process all tool calls
            logger.info("Handling tool calls with Composio")
            print("Handling tool calls with Composio")
            tool_results_list = await asyncio.to_thread(toolset.handle_tool_calls, response)
            logger.info(f"Received {len(tool_results_list)} tool results")
            print(f"Received {len(tool_results_list)} tool results")

            for i, tool_call in enumerate(tool_calls):
                if i < len(tool_results_list):
                    raw_result = tool_results_list[i]
                    logger.info(f"Processing result for tool call {i+1}/{len(tool_calls)}")
                    
                    # Track tool results
                    tool_result_info = {
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "result": raw_result
                    }
                    tool_results_received.append(tool_result_info)
                    
                    # Process tool result
                    tool_name = tool_call.function.name
                    result_content = _format_tool_result(raw_result)
                    logger.debug(f"Formatted result length: {len(result_content)}")
                    print(f"Result for {tool_name}: {result_content[:200]}...")
                    
                    messages.append({
                        "tool_call_id": tool_call.id, 
                        "role": "tool", 
                        "name": tool_name, 
                        "content": result_content
                    })
                    
                    # Extract leads from tool result
                    logger.info(f"Extracting leads from {tool_name} result")
                    leads = _extract_leads_from_tool_result(result_content)
                    if leads:
                        logger.info(f"Found {len(leads)} leads in tool result")
                        print(f"Found {len(leads)} leads in tool result")
                        all_leads.extend(leads)
                    else:
                        logger.info("No leads found in tool result")
                        print("No leads found in tool result")
                        
        except Exception as e:
            logger.error(f"Error in loop {loop_count}: {str(e)}", exc_info=True)
            print(f"Error in loop {loop_count}: {str(e)}")
            final_content = f"Error: {str(e)}"
            break        

    logger.info(f"Search completed with {len(all_leads)} total leads found")
    print(f"Search completed with {len(all_leads)} total leads found")
    
    response_data = {"leads": all_leads}
    
    
    return response_data


