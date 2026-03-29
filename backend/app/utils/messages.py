"""
Internationalization messages for API responses.
Supports English and Chinese.
"""
from flask import request


def get_request_language():
    """Get language from Accept-Language header, default to 'en'."""
    lang = request.headers.get('Accept-Language', 'en')
    if lang.startswith('zh'):
        return 'zh'
    return 'en'


MESSAGES = {
    # Project messages
    'project_not_found': {
        'en': 'Project not found: {id}',
        'zh': '项目不存在: {id}'
    },
    'project_deleted': {
        'en': 'Project deleted: {id}',
        'zh': '项目已删除: {id}'
    },
    'project_delete_failed': {
        'en': 'Project not found or delete failed: {id}',
        'zh': '项目不存在或删除失败: {id}'
    },
    'project_reset': {
        'en': 'Project reset: {id}',
        'zh': '项目已重置: {id}'
    },
    'missing_simulation_requirement': {
        'en': 'Please provide simulation_requirement',
        'zh': '请提供模拟需求描述 (simulation_requirement)'
    },
    'missing_files': {
        'en': 'Please upload at least one document file',
        'zh': '请至少上传一个文档文件'
    },
    'no_docs_processed': {
        'en': 'No documents were processed successfully. Please check file formats.',
        'zh': '没有成功处理任何文档，请检查文件格式'
    },
    'ontology_complete': {
        'en': 'Ontology generated: {entity_count} entity types, {edge_count} relation types',
        'zh': '本体生成完成: {entity_count} 个实体类型, {edge_count} 个关系类型'
    },
    'graph_build_started': {
        'en': 'Graph build task started',
        'zh': '图谱构建任务已启动'
    },
    'missing_project_id': {
        'en': 'Please provide project_id',
        'zh': '请提供 project_id'
    },
    'ontology_not_generated': {
        'en': 'Ontology not generated yet. Please call /ontology/generate first.',
        'zh': '项目尚未生成本体，请先调用 /ontology/generate'
    },
    'graph_building_in_progress': {
        'en': 'Graph is being built. Do not resubmit. To force rebuild, add force: true.',
        'zh': '图谱正在构建中，请勿重复提交。如需强制重建，请添加 force: true'
    },
    'graph_deleted': {
        'en': 'Graph deleted: {id}',
        'zh': '图谱已删除: {id}'
    },
    'task_not_found': {
        'en': 'Task not found: {id}',
        'zh': '任务不存在: {id}'
    },
    # Simulation messages
    'missing_simulation_id': {
        'en': 'Please provide simulation_id',
        'zh': '请提供 simulation_id'
    },
    'simulation_not_found': {
        'en': 'Simulation not found: {id}',
        'zh': '模拟不存在: {id}'
    },
    'graph_not_built': {
        'en': 'Graph not built yet for this project',
        'zh': '项目尚未构建图谱'
    },
    'zep_not_configured': {
        'en': 'ZEP_API_KEY not configured',
        'zh': 'ZEP_API_KEY未配置'
    },
    'graph_backend_not_configured': {
        'en': (
            'Graph backend is not configured correctly. '
            'For GRAPH_BACKEND=zep_cloud set ZEP_API_KEY; '
            'for graphiti_local set NEO4J_* and related variables (see .env.example).'
        ),
        'zh': (
            '图谱后端未正确配置。GRAPH_BACKEND=zep_cloud 时需配置 ZEP_API_KEY；'
            'graphiti_local 时需配置 NEO4J 等变量（见 .env.example）。'
        ),
    },
    'entity_not_found': {
        'en': 'Entity not found: {id}',
        'zh': '实体不存在: {id}'
    },
    # Report messages
    'report_task_started': {
        'en': 'Report generation task started',
        'zh': '报告生成任务已启动'
    },
    'report_already_generated': {
        'en': 'Report already generated',
        'zh': '报告已生成'
    },
    'report_not_found': {
        'en': 'Report not found',
        'zh': '报告不存在'
    },
    'report_deleted': {
        'en': 'Report deleted: {id}',
        'zh': '报告已删除: {id}'
    },
    'report_generation_failed': {
        'en': 'Report generation failed',
        'zh': '报告生成失败'
    },
    'missing_requirement': {
        'en': 'Missing simulation requirement description',
        'zh': '缺少模拟需求描述'
    },
    'missing_graph_id': {
        'en': 'Missing graph ID',
        'zh': '缺少图谱ID'
    },
    'init_report_agent': {
        'en': 'Initializing Report Agent...',
        'zh': '初始化Report Agent...'
    },
    'report_task_started_long': {
        'en': 'Report generation task started. Check progress via /api/report/generate/status.',
        'zh': '报告生成任务已启动，请通过 /api/report/generate/status 查询进度'
    },
    # Config messages
    'llm_not_configured': {
        'en': 'LLM_API_KEY not configured',
        'zh': 'LLM_API_KEY 未配置'
    },
    'llm_auth_failed': {
        'en': 'LLM API authentication failed. Check LLM_API_KEY and LLM_BASE_URL in your environment (for example .env) match your provider.',
        'zh': '大模型 API 鉴权失败，请检查环境变量中的 LLM_API_KEY 与 LLM_BASE_URL（如 .env）是否与服务商一致。'
    },
    'zep_not_configured_config': {
        'en': 'ZEP_API_KEY not configured',
        'zh': 'ZEP_API_KEY 未配置'
    },
    # Graph build progress messages
    'init_graph_service': {
        'en': 'Initializing graph build service...',
        'zh': '初始化图谱构建服务...'
    },
    'text_chunking': {
        'en': 'Text chunking...',
        'zh': '文本分块中...'
    },
    'graph_build_complete': {
        'en': 'Graph build complete',
        'zh': '图谱构建完成'
    },
    'text_extraction_complete': {
        'en': 'Text extraction complete, {length} characters total',
        'zh': '文本提取完成，共 {length} 字符'
    },
    'calling_llm': {
        'en': 'Calling LLM to generate ontology...',
        'zh': '调用 LLM 生成本体定义...'
    },
    # Interview prompt
    'interview_prefix': {
        'en': 'Based on your persona, all past memories and actions, respond directly with text without calling any tools: ',
        'zh': '结合你的人设、所有的过往记忆与行动，不调用任何工具直接用文本回复我：'
    },
    'agent_responding': {
        'en': 'Agent responding...',
        'zh': 'Agent回复...'
    },
    'default_question': {
        'en': 'Please explain the public opinion trends',
        'zh': '请解释一下舆情走向'
    },
    'interview_env_not_running': {
        'en': (
            'The simulation environment is not running or has been closed. '
            'Make sure the simulation has finished and is waiting for commands.'
        ),
        'zh': '模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。',
    },
}


def msg(key, lang=None, **kwargs):
    """Get a translated message by key.

    Args:
        key: Message key
        lang: Language code ('en' or 'zh'). If None, reads from request header.
        **kwargs: Format arguments

    Returns:
        Translated and formatted message string
    """
    if lang is None:
        try:
            lang = get_request_language()
        except RuntimeError:
            # Outside of request context (e.g., background threads)
            lang = 'en'

    message_dict = MESSAGES.get(key, {})
    template = message_dict.get(lang, message_dict.get('en', key))

    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template
