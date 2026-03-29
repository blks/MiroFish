"""Configuration management utilities."""

import os
from dotenv import load_dotenv



project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    
    load_dotenv(override=True)


class Config:
    """Config."""
    
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    
    JSON_AS_ASCII = False
    
    
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
    
    
    GRAPH_BACKEND = os.environ.get('GRAPH_BACKEND', 'zep_cloud').strip().lower()

    
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')

    
    NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
    NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE', 'neo4j')

    GRAPHITI_AUTO_INIT = os.environ.get('GRAPHITI_AUTO_INIT', 'True').lower() == 'true'
    GRAPHITI_TELEMETRY_ENABLED = os.environ.get('GRAPHITI_TELEMETRY_ENABLED', 'False').lower() == 'true'
    GRAPHITI_MAX_COROUTINES = int(os.environ.get('GRAPHITI_MAX_COROUTINES', '10'))
    GRAPHITI_SEARCH_RERANKER = os.environ.get('GRAPHITI_SEARCH_RERANKER', 'rrf').strip().lower()

    GRAPHITI_LLM_API_KEY = os.environ.get('GRAPHITI_LLM_API_KEY') or LLM_API_KEY
    GRAPHITI_LLM_BASE_URL = os.environ.get('GRAPHITI_LLM_BASE_URL') or LLM_BASE_URL
    GRAPHITI_LLM_MODEL = os.environ.get('GRAPHITI_LLM_MODEL') or LLM_MODEL_NAME

    GRAPHITI_EMBEDDER_API_KEY = os.environ.get('GRAPHITI_EMBEDDER_API_KEY') or LLM_API_KEY
    GRAPHITI_EMBEDDER_BASE_URL = os.environ.get('GRAPHITI_EMBEDDER_BASE_URL') or LLM_BASE_URL
    GRAPHITI_EMBEDDER_MODEL = os.environ.get('GRAPHITI_EMBEDDER_MODEL', 'text-embedding-3-small')

    GRAPHITI_RERANKER_API_KEY = os.environ.get('GRAPHITI_RERANKER_API_KEY') or LLM_API_KEY
    GRAPHITI_RERANKER_BASE_URL = os.environ.get('GRAPHITI_RERANKER_BASE_URL') or LLM_BASE_URL
    GRAPHITI_RERANKER_MODEL = os.environ.get('GRAPHITI_RERANKER_MODEL') or LLM_MODEL_NAME
    
    
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    
    DEFAULT_CHUNK_SIZE = 500  
    DEFAULT_CHUNK_OVERLAP = 50  
    
    
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))
    
    @classmethod
    def validate_graph_backend(cls):
        """Validate Graph Backend."""
        errors = []

        if cls.GRAPH_BACKEND == 'zep_cloud':
            if not cls.ZEP_API_KEY:
                errors.append("ZEP_API_KEY is not configured")
        elif cls.GRAPH_BACKEND == 'graphiti_local':
            if not cls.NEO4J_URI:
                errors.append("NEO4J_URI is not configured")
            if not cls.NEO4J_USER:
                errors.append("NEO4J_USER is not configured")
            if not cls.NEO4J_PASSWORD:
                errors.append("NEO4J_PASSWORD is not configured")
            if not cls.GRAPHITI_LLM_API_KEY:
                errors.append("GRAPHITI_LLM_API_KEY/LLM_API_KEY is not configured")
            if not cls.GRAPHITI_EMBEDDER_API_KEY:
                errors.append("GRAPHITI_EMBEDDER_API_KEY/LLM_API_KEY is not configured")
        else:
            errors.append(f"Unsupported GRAPH_BACKEND: {cls.GRAPH_BACKEND}")

        return errors

    @classmethod
    def validate(cls):
        """Validate the configuration."""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is not configured")
        errors.extend(cls.validate_graph_backend())
        return errors
