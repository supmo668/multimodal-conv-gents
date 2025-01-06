from pydantic import BaseModel, Field
from typing import Optional

from langchain.output_parsers import PydanticOutputParser

# Definition of TraitScore used across all metrics
class TraitScore(BaseModel):
    score: Optional[int] = Field(
        None, ge=1, le=5, 
        description="The score for the trait ranging from 1 (Very Low) to 5 (Very High). This score reflects the degree to which the character demonstrates this trait during the interaction. "
                    "1 indicates minimal expression, while 5 indicates a strong presence of the trait. If insufficient information is provided, this field can be None."
    )
    justification: Optional[str] = Field(
        None, 
        description="Provide a detailed justification for the score, citing specific behaviors, language, or reactions from the character observed during the interaction. "
                    "If insufficient information is provided, this field can be None."
    )

# Behavioral Economics metrics for a character
class BehavioralEconomicsMetrics(BaseModel):
    decision_making_style: Optional[TraitScore] = Field(
        None, 
        description="Score measuring the character’s decision-making process. A lower score reflects a tendency towards fast, heuristic-driven decisions (System 1 thinking), while a higher score reflects more rational, deliberate decisions (System 2 thinking)."
    )
    risk_tolerance: Optional[TraitScore] = Field(
        None, 
        description="Score indicating the character's risk preferences. A lower score reflects risk-aversion, while a higher score indicates risk-seeking behavior, based on Prospect Theory."
    )
    collaboration_preference: Optional[TraitScore] = Field(
        None, 
        description="Score measuring the character’s preference for autonomy (lower score) vs. teamwork (higher score). Based on industrial-organizational research on group dynamics and work preferences."
    )
    cognitive_bias_tendency: Optional[TraitScore] = Field(
        None, 
        description="Score reflecting the character's susceptibility to cognitive biases such as confirmation bias, status quo bias, and framing effects. A lower score reflects high susceptibility to biases, while a higher score indicates a tendency for more objective, bias-free thinking."
    )

# Cognitive Compatibility metrics for a character
class CognitiveCompatibility(BaseModel):
    communication_style: Optional[TraitScore] = Field(
        None, 
        description="Evaluates the similarity between the character’s communication style and that of the known character."
    )
    problem_solving_approach: Optional[TraitScore] = Field(
        None, 
        description="Assesses the similarity in how the character approaches solving problems compared to the known character."
    )
    emotional_intelligence: Optional[TraitScore] = Field(
        None, 
        description="Measures the degree to which the character and the known character are able to perceive, interpret, and manage emotions."
    )
    values_alignment: Optional[TraitScore] = Field(
        None, 
        description="Evaluates the similarity in values (e.g., loyalty, justice, fairness) between the character and the known character."
    )

# Industrial Compatibility metrics for a character
class IndustrialCompatibilityMetrics(BaseModel):
    communication_alignment: Optional[TraitScore] = Field(
        None, 
        description="Measures how well the character’s communication style aligns with others in terms of directness, formality, and clarity. A higher score reflects stronger alignment."
    )
    decision_conflict_handling: Optional[TraitScore] = Field(
        None, 
        description="Measures how well the character handles decision-making conflict in group settings. A higher score indicates better resolution and collaborative approach, while a lower score indicates higher conflict sensitivity."
    )
    trust_in_group_settings: Optional[TraitScore] = Field(
        None, 
        description="Quantifies how much the character is trusted by others in a professional setting, considering their reliability and integrity in social and group interactions. A higher score reflects higher levels of trust."
    )

# Final Interactibility evaluation for a character
class InteractibilityEvaluationResult(BaseModel):
    character_name: str = Field(..., description="The name of the character being evaluated.")
    behavioral_metrics: Optional[BehavioralEconomicsMetrics] = Field(
        None, 
        description="Behavioral economics-based metrics assessing decision-making style, risk tolerance, collaboration preferences, and cognitive biases. If insufficient information is provided, this field can be None."
    )
    cognitive_compatibility: Optional[CognitiveCompatibility] = Field(
        None, 
        description="Metrics assessing cognitive compatibility with the known character, including communication style, problem-solving approach, emotional intelligence, and values alignment. If insufficient information is provided, this field can be None."
    )
    industrial_compatibility: Optional[IndustrialCompatibilityMetrics] = Field(
        None, 
        description="Metrics evaluating the character's communication alignment, conflict-handling, and trust in group settings. If insufficient information is provided, this field can be None."
    )

# partial parsers
behavioral_assessment_parser = PydanticOutputParser(pydantic_object=BehavioralEconomicsMetrics)
compatibility_assessment_parser = PydanticOutputParser(pydantic_object=IndustrialCompatibilityMetrics)

# full parsers
interactivability_assessment_parser = PydanticOutputParser(pydantic_object=InteractibilityEvaluationResult)