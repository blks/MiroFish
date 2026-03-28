"""
本体生成服务
接口1：分析文本内容，生成适合社会模拟的实体和关系类型定义
"""

import json
import re
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


_ENTITY_NAME_KEYS = (
    "name",
    "type",
    "label",
    "entity_type",
    "english_name",
    "class_name",
    "title",
)
_EDGE_NAME_KEYS = (
    "name",
    "type",
    "label",
    "relation",
    "relation_type",
    "edge_type",
    "relationship",
)
_NAME_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "for",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "at",
        "any",
        "who",
        "can",
        "that",
        "this",
        "with",
        "from",
        "as",
        "is",
        "are",
        "be",
        "their",
        "they",
        "by",
        "not",
        "may",
        "must",
        "each",
        "all",
        "when",
        "used",
        "using",
        "type",
        "entity",
        "role",
        "one",
        "other",
    }
)


def _extract_pascal_identifier(text: str, max_words: int = 3) -> str:
    """Build PascalCase from English tokens in arbitrary text (Zep-friendly)."""
    if not text or not isinstance(text, str):
        return ""
    words = re.findall(r"[A-Za-z][a-zA-Z0-9]*", text)
    parts: List[str] = []
    for w in words:
        lw = w.lower()
        if lw in _NAME_STOPWORDS:
            continue
        parts.append(w[0].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        if len(parts) >= max_words:
            break
    return "".join(parts)


def _extract_upper_snake_identifier(text: str, max_words: int = 3) -> str:
    """Build UPPER_SNAKE_CASE from English tokens for edge type names."""
    if not text or not isinstance(text, str):
        return ""
    words = re.findall(r"[A-Za-z][a-zA-Z0-9]*", text)
    parts: List[str] = []
    for w in words:
        lw = w.lower()
        if lw in _NAME_STOPWORDS:
            continue
        parts.append(lw.upper())
        if len(parts) >= max_words:
            break
    return "_".join(parts)


def _first_string_example(examples: Any) -> str:
    if not isinstance(examples, list):
        return ""
    for e in examples:
        if isinstance(e, str) and e.strip():
            return e.strip()
    return ""


def _coerce_ontology_item_name(item: Dict[str, Any], kind: str, index: int) -> str:
    """
    Resolve a non-empty type name. The LLM often omits `name` but fills
    description/examples or uses alternate keys (`type`, `label`, ...).
    """
    is_entity = kind == "Entity"
    keys = _ENTITY_NAME_KEYS if is_entity else _EDGE_NAME_KEYS
    for key in keys:
        raw = item.get(key)
        if isinstance(raw, str):
            s = raw.strip()
            if s:
                return s

    ex = _first_string_example(item.get("examples"))
    if ex:
        if is_entity:
            inferred = _extract_pascal_identifier(ex, max_words=2)
            if len(inferred) >= 3:
                return inferred
        else:
            inferred = _extract_upper_snake_identifier(ex, max_words=3)
            if len(inferred) >= 4:
                return inferred

    desc = item.get("description", "")
    if isinstance(desc, str) and desc.strip():
        if is_entity:
            inferred = _extract_pascal_identifier(desc, max_words=3)
            if len(inferred) >= 4:
                return inferred
        else:
            inferred = _extract_upper_snake_identifier(desc, max_words=3)
            if len(inferred) >= 4:
                return inferred

    if is_entity:
        return f"InferredEntityType{index + 1}"
    return f"INFERRED_RELATION_{index + 1}"


# 本体生成的系统提示词
ONTOLOGY_SYSTEM_PROMPT = """你是一个专业的知识图谱本体设计专家。你的任务是分析给定的文本内容和模拟需求，设计适合**社交媒体舆论模拟**的实体类型和关系类型。

**重要：你必须输出有效的JSON格式数据，不要输出任何其他内容。**

## 核心任务背景

我们正在构建一个**社交媒体舆论模拟系统**。在这个系统中：
- 每个实体都是一个可以在社交媒体上发声、互动、传播信息的"账号"或"主体"
- 实体之间会相互影响、转发、评论、回应
- 我们需要模拟舆论事件中各方的反应和信息传播路径

因此，**实体必须是现实中真实存在的、可以在社媒上发声和互动的主体**：

**可以是**：
- 具体的个人（公众人物、当事人、意见领袖、专家学者、普通人）
- 公司、企业（包括其官方账号）
- 组织机构（大学、协会、NGO、工会等）
- 政府部门、监管机构
- 媒体机构（报纸、电视台、自媒体、网站）
- 社交媒体平台本身
- 特定群体代表（如校友会、粉丝团、维权群体等）

**不可以是**：
- 抽象概念（如"舆论"、"情绪"、"趋势"）
- 主题/话题（如"学术诚信"、"教育改革"）
- 观点/态度（如"支持方"、"反对方"）

## 输出格式

请输出JSON格式，包含以下结构：

```json
{
    "entity_types": [
        {
            "name": "实体类型名称（英文，PascalCase）",
            "description": "简短描述（英文，不超过100字符）",
            "attributes": [
                {
                    "name": "属性名（英文，snake_case）",
                    "type": "text",
                    "description": "属性描述"
                }
            ],
            "examples": ["示例实体1", "示例实体2"]
        }
    ],
    "edge_types": [
        {
            "name": "关系类型名称（英文，UPPER_SNAKE_CASE）",
            "description": "简短描述（英文，不超过100字符）",
            "source_targets": [
                {"source": "源实体类型", "target": "目标实体类型"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "对文本内容的简要分析说明（中文）"
}
```

## 设计指南（极其重要！）

### 0. 命名规则（极其重要，勿省略）

- `entity_types` 与 `edge_types` 中的**每一条**都必须包含 JSON 字段 **`name`**（键名必须完全一致）。禁止只用 `type`、`label`、中文标题或 description 代替标识符。
- 每个 `name` 必须是**可读、可理解的英文**：例如 `NationalFilmAgency`、`PublishingCompany`。禁止：空字符串、纯空白、`Type1`、`CategoryA`、`Unnamed*` 等占位符。
- 前 8 个实体类型应来自**文档与模拟需求中真实出现或隐含的角色/机构类别**，避免空洞的泛化桶。
- 关系类型的 `name` 必须为 **UPPER_SNAKE_CASE**，且语义清晰（如 `HAS_PUBLICATION_RIGHTS`），禁止 `REL1` 这类占位。

### 1. 实体类型设计 - 必须严格遵守

**数量要求：必须正好10个实体类型**

**层次结构要求（必须同时包含具体类型和兜底类型）**：

你的10个实体类型必须包含以下层次：

A. **兜底类型（必须包含，放在列表最后2个）**：
   - `Person`: 任何自然人个体的兜底类型。当一个人不属于其他更具体的人物类型时，归入此类。
   - `Organization`: 任何组织机构的兜底类型。当一个组织不属于其他更具体的组织类型时，归入此类。

B. **具体类型（8个，根据文本内容设计）**：
   - 针对文本中出现的主要角色，设计更具体的类型
   - 例如：如果文本涉及学术事件，可以有 `Student`, `Professor`, `University`
   - 例如：如果文本涉及商业事件，可以有 `Company`, `CEO`, `Employee`

**为什么需要兜底类型**：
- 文本中会出现各种人物，如"中小学教师"、"路人甲"、"某位网友"
- 如果没有专门的类型匹配，他们应该被归入 `Person`
- 同理，小型组织、临时团体等应该归入 `Organization`

**具体类型的设计原则**：
- 从文本中识别出高频出现或关键的角色类型
- 每个具体类型应该有明确的边界，避免重叠
- description 必须清晰说明这个类型和兜底类型的区别

### 2. 关系类型设计

- 数量：6-10个
- 关系应该反映社媒互动中的真实联系
- 确保关系的 source_targets 涵盖你定义的实体类型

### 3. 属性设计

- 每个实体类型1-3个关键属性
- **注意**：属性名不能使用 `name`、`uuid`、`group_id`、`created_at`、`summary`（这些是系统保留字）
- 推荐使用：`full_name`, `title`, `role`, `position`, `location`, `description` 等

## 实体类型参考

**个人类（具体）**：
- Student: 学生
- Professor: 教授/学者
- Journalist: 记者
- Celebrity: 明星/网红
- Executive: 高管
- Official: 政府官员
- Lawyer: 律师
- Doctor: 医生

**个人类（兜底）**：
- Person: 任何自然人（不属于上述具体类型时使用）

**组织类（具体）**：
- University: 高校
- Company: 公司企业
- GovernmentAgency: 政府机构
- MediaOutlet: 媒体机构
- Hospital: 医院
- School: 中小学
- NGO: 非政府组织

**组织类（兜底）**：
- Organization: 任何组织机构（不属于上述具体类型时使用）

## 关系类型参考

- WORKS_FOR: 工作于
- STUDIES_AT: 就读于
- AFFILIATED_WITH: 隶属于
- REPRESENTS: 代表
- REGULATES: 监管
- REPORTS_ON: 报道
- COMMENTS_ON: 评论
- RESPONDS_TO: 回应
- SUPPORTS: 支持
- OPPOSES: 反对
- COLLABORATES_WITH: 合作
- COMPETES_WITH: 竞争
"""

ONTOLOGY_SYSTEM_PROMPT_EN = """You are a professional knowledge graph ontology design expert. Your task is to analyze the given text content and simulation requirements, and design entity types and relationship types suitable for **social media public opinion simulation**.

**Important: You must output valid JSON format data. Do not output anything else.**

## Core Task Background

We are building a **social media public opinion simulation system**. In this system:
- Each entity is an "account" or "agent" that can speak, interact, and spread information on social media
- Entities influence each other through forwarding, commenting, and responding
- We need to simulate the reactions of various parties and the information propagation paths during public opinion events

Therefore, **entities must be real-world agents that can speak and interact on social media**:

**Acceptable**:
- Specific individuals (public figures, parties involved, opinion leaders, scholars, ordinary people)
- Companies and enterprises (including their official accounts)
- Organizations and institutions (universities, associations, NGOs, unions, etc.)
- Government departments and regulatory agencies
- Media organizations (newspapers, TV stations, self-media, websites)
- Social media platforms themselves
- Representatives of specific groups (e.g., alumni associations, fan groups, advocacy groups, etc.)

**Not acceptable**:
- Abstract concepts (e.g., "public opinion", "sentiment", "trend")
- Topics/themes (e.g., "academic integrity", "education reform")
- Viewpoints/attitudes (e.g., "supporters", "opponents")

## Output Format

Please output in JSON format with the following structure:

```json
{
    "entity_types": [
        {
            "name": "Entity type name (English, PascalCase)",
            "description": "Brief description (English, no more than 100 characters)",
            "attributes": [
                {
                    "name": "attribute_name (English, snake_case)",
                    "type": "text",
                    "description": "Attribute description"
                }
            ],
            "examples": ["Example entity 1", "Example entity 2"]
        }
    ],
    "edge_types": [
        {
            "name": "Relationship type name (English, UPPER_SNAKE_CASE)",
            "description": "Brief description (English, no more than 100 characters)",
            "source_targets": [
                {"source": "Source entity type", "target": "Target entity type"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis summary of the text content (in English)"
}
```

## Design Guidelines (Extremely Important!)

### 0. Naming Rules (Critical — Do Not Skip)

- Every entry in `entity_types` and `edge_types` MUST include a JSON field **`name`** (exact key spelling). Do not use only `type`, `label`, non-English titles, or `description` alone as the identifier.
- Each `name` must be **human-meaningful English**: e.g. `NationalFilmAgency`, `PublishingCompany`. Forbidden: empty string, whitespace-only, `Type1`, `CategoryA`, `Unnamed*`, or other placeholders.
- The first 8 entity types should name **concrete actor categories** grounded in the documents and simulation brief (institutions, professions, venues), not empty generic buckets.
- Each relationship `name` must be **UPPER_SNAKE_CASE** and descriptive (e.g. `HAS_PUBLICATION_RIGHTS`), not `REL1` or similar placeholders.

### 1. Entity Type Design - Must Be Strictly Followed

**Quantity requirement: Exactly 10 entity types**

**Hierarchy requirements (must include both specific types and fallback types)**:

Your 10 entity types must include the following layers:

A. **Fallback types (must include, placed at the end of the list)**:
   - `Person`: Fallback type for any natural person. When a person does not belong to other more specific person types, classify them here.
   - `Organization`: Fallback type for any organization. When an organization does not belong to other more specific organization types, classify it here.

B. **Specific types (8, designed based on text content)**:
   - Design more specific types for the main roles appearing in the text
   - Example: If the text involves academic events, you can have `Student`, `Professor`, `University`
   - Example: If the text involves business events, you can have `Company`, `CEO`, `Employee`

**Why fallback types are needed**:
- Various people appear in the text, such as "elementary school teachers", "bystanders", "some netizen"
- If there is no specific type match, they should be classified as `Person`
- Similarly, small organizations, temporary groups, etc. should be classified as `Organization`

**Design principles for specific types**:
- Identify high-frequency or key role types from the text
- Each specific type should have clear boundaries to avoid overlap
- The description must clearly explain the difference between this type and the fallback type

### 2. Relationship Type Design

- Quantity: 6-10
- Relationships should reflect real connections in social media interactions
- Ensure that the source_targets of relationships cover your defined entity types

### 3. Attribute Design

- 1-3 key attributes per entity type
- **Note**: Attribute names cannot use `name`, `uuid`, `group_id`, `created_at`, `summary` (these are system reserved words)
- Recommended: `full_name`, `title`, `role`, `position`, `location`, `description`, etc.

## Entity Type Reference

**Individual (specific)**:
- Student: Student
- Professor: Professor/Scholar
- Journalist: Journalist
- Celebrity: Celebrity/Influencer
- Executive: Executive
- Official: Government official
- Lawyer: Lawyer
- Doctor: Doctor

**Individual (fallback)**:
- Person: Any natural person (used when not belonging to the above specific types)

**Organization (specific)**:
- University: University/College
- Company: Company/Enterprise
- GovernmentAgency: Government agency
- MediaOutlet: Media organization
- Hospital: Hospital
- School: Elementary/Secondary school
- NGO: Non-governmental organization

**Organization (fallback)**:
- Organization: Any organization (used when not belonging to the above specific types)

## Relationship Type Reference

- WORKS_FOR: Works for
- STUDIES_AT: Studies at
- AFFILIATED_WITH: Affiliated with
- REPRESENTS: Represents
- REGULATES: Regulates
- REPORTS_ON: Reports on
- COMMENTS_ON: Comments on
- RESPONDS_TO: Responds to
- SUPPORTS: Supports
- OPPOSES: Opposes
- COLLABORATES_WITH: Collaborates with
- COMPETES_WITH: Competes with
"""


class OntologyGenerator:
    """
    本体生成器
    分析文本内容，生成实体和关系类型定义
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        生成本体定义

        Args:
            document_texts: 文档文本列表
            simulation_requirement: 模拟需求描述
            additional_context: 额外上下文
            language: 语言选择，'en' 为英文，'zh' 为中文

        Returns:
            本体定义（entity_types, edge_types等）
        """
        # 构建用户消息
        user_message = self._build_user_message(
            document_texts,
            simulation_requirement,
            additional_context,
            language=language
        )

        system_prompt = ONTOLOGY_SYSTEM_PROMPT_EN if language == 'en' else ONTOLOGY_SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 调用LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        # 验证和后处理
        result = self._validate_and_process(result)
        
        return result
    
    # 传给 LLM 的文本最大长度（5万字）
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str],
        language: str = 'en'
    ) -> str:
        """构建用户消息"""

        # 合并文本
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)

        # 如果文本超过5万字，截断（仅影响传给LLM的内容，不影响图谱构建）
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            if language == 'en':
                combined_text += f"\n\n...(Original text has {original_length} characters, truncated to first {self.MAX_TEXT_LENGTH_FOR_LLM} characters for ontology analysis)..."
            else:
                combined_text += f"\n\n...(原文共{original_length}字，已截取前{self.MAX_TEXT_LENGTH_FOR_LLM}字用于本体分析)..."

        if language == 'en':
            message = f"""## Simulation Requirement

{simulation_requirement}

## Document Content

{combined_text}
"""

            if additional_context:
                message += f"""
## Additional Notes

{additional_context}
"""

            message += """
Based on the above content, design entity types and relationship types suitable for social media public opinion simulation.

**Rules that must be followed**:
1. You must output exactly 10 entity types
2. The last 2 must be fallback types: Person (individual fallback) and Organization (organization fallback)
3. The first 8 are specific types designed based on the text content
4. All entity types must be real-world agents that can speak on social media, not abstract concepts
5. Attribute names cannot use reserved words like name, uuid, group_id; use full_name, org_name, etc. instead
6. Every entity_types[i] and edge_types[i] object MUST include a non-empty, meaningful English `name` (PascalCase for entities, UPPER_SNAKE_CASE for edges). Never omit `name` or leave it blank.
"""
        else:
            message = f"""## 模拟需求

{simulation_requirement}

## 文档内容

{combined_text}
"""

            if additional_context:
                message += f"""
## 额外说明

{additional_context}
"""

            message += """
请根据以上内容，设计适合社会舆论模拟的实体类型和关系类型。

**必须遵守的规则**：
1. 必须正好输出10个实体类型
2. 最后2个必须是兜底类型：Person（个人兜底）和 Organization（组织兜底）
3. 前8个是根据文本内容设计的具体类型
4. 所有实体类型必须是现实中可以发声的主体，不能是抽象概念
5. 属性名不能使用 name、uuid、group_id 等保留字，用 full_name、org_name 等替代
6. 每个 entity_types 与 edge_types 对象必须包含非空且有语义的英文 `name`（实体用 PascalCase，关系用 UPPER_SNAKE_CASE），禁止省略或留空
"""

        return message
    
    def _normalize_ontology_items(
        self, items: List[Any], kind: str
    ) -> List[Dict[str, Any]]:
        """
        LLM JSON may omit 'name' on entity_types / edge_types entries, which would
        raise KeyError later. Coerce to dicts with a non-empty name.
        """
        normalized: List[Dict[str, Any]] = []
        for i, item in enumerate(items or []):
            if not isinstance(item, dict):
                continue
            name = _coerce_ontology_item_name(item, kind, i)
            normalized.append({**item, "name": name})
        return normalized

    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证和后处理结果"""
        
        # 确保必要字段存在
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""

        result["entity_types"] = self._normalize_ontology_items(
            result["entity_types"], "Entity"
        )
        result["edge_types"] = self._normalize_ontology_items(
            result["edge_types"], "Relation"
        )
        
        # 验证实体类型
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # 确保description不超过100字符
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # 验证关系类型
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API 限制：最多 10 个自定义实体类型，最多 10 个自定义边类型
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        # 兜底类型定义
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # 检查是否已有兜底类型
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # 需要添加的兜底类型
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # 如果添加后会超过 10 个，需要移除一些现有类型
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # 计算需要移除多少个
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # 从末尾移除（保留前面更重要的具体类型）
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # 添加兜底类型
            result["entity_types"].extend(fallbacks_to_add)
        
        # 最终确保不超过限制（防御性编程）
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        将本体定义转换为Python代码（类似ontology.py）
        
        Args:
            ontology: 本体定义
            
        Returns:
            Python代码字符串
        """
        code_lines = [
            '"""',
            '自定义实体类型定义',
            '由MiroFish自动生成，用于社会舆论模拟',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== 实体类型定义 ==============',
            '',
        ]
        
        # 生成实体类型
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== 关系类型定义 ==============')
        code_lines.append('')
        
        # 生成关系类型
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # 转换为PascalCase类名
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # 生成类型字典
        code_lines.append('# ============== 类型配置 ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # 生成边的source_targets映射
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)

