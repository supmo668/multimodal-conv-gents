from pydantic import BaseModel, Field
from typing import Literal, Optional

from thought_agents.ontology.config.dialogue import Person
from langchain.output_parsers import PydanticOutputParser

# 1. Personality Traits (Big Five Model)

class TraitScore(BaseModel):
    score: Optional[int] = Field(
      None, ge=1, le=5, description="The score for the trait ranging from 1 (Very Low) to 5 (Very High). This score reflects the degree to which the character demonstrates this trait during the interaction. 1 indicates minimal expression, while 5 indicates a strong presence of the trait. If insufficient information is provided, this field can be None."
    )
    justification: Optional[str] = Field(
      ..., description="Provide a detailed justification for the score, citing specific behaviors, language, or reactions from the character observed during the interaction. If insufficient information is provided, this field can be None."
    )

class PersonalityTraits(BaseModel):
    openness: TraitScore = Field(
      ..., description="Measures the degree to which the character is willing to engage with new ideas, experiences, and creative thinking."
    )
    conscientiousness: TraitScore = Field(
      ..., description="Assesses the individual's degree of organization, dependability, and attention to detail."
    )
    extraversion: TraitScore = Field(
      ..., description="Captures the extent to which the character seeks stimulation from social interactions and enjoys being in the company of others."
    )
    agreeableness: TraitScore = Field( description="Measures the character's tendencies toward cooperation, trust, and empathy.")
    neuroticism: TraitScore = Field(
      ..., description="Indicates the degree to which the character experiences emotional instability, anxiety, or moodiness.")

# 2. Character Traits

class CharacterTraits(BaseModel):
    honesty: TraitScore = Field(
      ..., description="Evaluates the extent to which the character values truthfulness and transparency in their behavior and communication.")
    integrity: TraitScore = Field(
      ..., description="Assesses adherence to moral principles and ethical standards.")
    empathy: TraitScore = Field(
      ..., description="Measures the character's capacity to understand and share the emotions of others.")
    loyalty: TraitScore = Field(
      ..., description="Assesses the degree of commitment the character shows to maintaining supportive and dependable relationships.")
    courage: TraitScore = Field(
      ..., description="Evaluates the character's ability to act in the face of fear or risk, especially when moral or ethical principles are at stake.")
    humility: TraitScore = Field(
      ..., description="Captures the character's ability to recognize their limitations and maintain modesty in interactions.")

# Traits & character analysis result
class CharacteristicAnalysisResult(BaseModel):
    person: Person
    personality_traits: PersonalityTraits
    character_traits: CharacterTraits

# MBTI
# The Myers-Briggs Type Indicator (MBTI) is one of the most widely used personality typologies
class DichotomyScore(BaseModel):
    score: Optional[float] = Field(
        None, ge=1, le=10, 
        description="Score represents the relative strength of each trait in the dichotomy. A higher score indicates a stronger presence of the first trait in the pair. Score ranges from 1 (pure second trait) to 10 (pure first trait). If insufficient information is provided, this field can be None."
    )
    justification: Optional[str] = Field(
        None, 
        description="Provide a detailed justification for the score, citing specific behaviors observed during the interaction. If insufficient information is available, this field can be None."
    )

class MBTITraits(BaseModel):
    extraversion_introversion: DichotomyScore = Field(
        None, 
        description="Measures whether the character tends to focus on external events and social interactions (Extraversion) or prefers internal thoughts and solitary activities (Introversion). If insufficient information is provided, this field can be None."
    )
    sensing_intuition: DichotomyScore = Field(
        None, 
        description="Assesses whether the character focuses on concrete, factual information (Sensing) or abstract concepts and patterns (Intuition). If insufficient information is provided, this field can be None."
    )
    thinking_feeling: DichotomyScore = Field(
        None, 
        description="Evaluates whether the character tends to make decisions based on logic and objective analysis (Thinking) or based on emotions and interpersonal harmony (Feeling). If insufficient information is provided, this field can be None."
    )
    judging_perceiving: DichotomyScore = Field(
        None, 
        description="Measures whether the character prefers structure and planning (Judging) or a flexible, adaptable approach to life (Perceiving). If insufficient information is provided, this field can be None."
    )

class MBTIEvaluationResult(BaseModel):
    name: str = Field(
      ..., description="The name of target character.")
    mbti_type: Literal[
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ] = Field(
      ..., description="The MBTI type inferred from the interaction.")
    mbti_traits: MBTITraits

# Full analysis result
class CharacterEvaluationResult(BaseModel):
    characteristic_analysis_result: CharacteristicAnalysisResult
    mbti_evaluation_result: MBTIEvaluationResult

# partial parsers
characteristic_assessment_parser = PydanticOutputParser(pydantic_object=CharacteristicAnalysisResult)
mbti_assessment_parser = PydanticOutputParser(pydantic_object=MBTIEvaluationResult)

# full parsers
character_assessment_parser = PydanticOutputParser(pydantic_object=CharacterEvaluationResult)
