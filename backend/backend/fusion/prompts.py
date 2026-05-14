"""
Fusion prompts module.
Contains prompt templates for LLM-based reasoning (if needed in future).
"""


class FusionPrompts:
    """
    Prompt templates for fusion layer reasoning.
    Currently minimal - can be extended for LLM-based constraint extraction.
    """
    
    REGULATION_EXTRACTION_PROMPT = """
    Extract structured constraints from the following building regulation text:
    
    {regulation_text}
    
    Return a JSON object with:
    - room_type: string
    - min_area_sqft: number
    - min_width_ft: number
    - setback_ft: number
    - ventilation_required: boolean
    """
    
    PATTERN_ANALYSIS_PROMPT = """
    Analyze the following layout patterns and extract common design principles:
    
    {pattern_descriptions}
    
    Identify:
    - Common room adjacencies
    - Typical area ratios
    - Layout patterns
    """
    
    LAYOUT_COMPOSITION_PROMPT = """
    Compose a semantic layout JSON from:
    - User requirements: {user_request}
    - Regulations: {regulations}
    - Patterns: {patterns}
    - Vaastu rules: {vaastu_rules}
    
    Output a structured layout specification.
    """

