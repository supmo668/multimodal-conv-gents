from pydantic import BaseModel, Field
from typing import Literal

# 1. Personality Traits (Big Five Model)

class TraitScore(BaseModel):
    score: int = Field(
      ..., ge=1, le=5, description="The score for the trait ranging from 1 (Very Low) to 5 (Very High). This score reflects the degree to which Person A demonstrates this trait during the interaction. 1 indicates minimal expression, while 5 indicates a strong presence of the trait."
    )
    justification: str = Field(
      ..., description="Provide a detailed justification for the score, citing specific behaviors, language, or reactions from Person A observed during the interaction."
    )

class PersonalityTraits(BaseModel):
    openness: TraitScore = Field(
      ..., description="Measures the degree to which Person A is willing to engage with new ideas, experiences, and creative thinking."
    )
    conscientiousness: TraitScore = Field(
      ..., description="Assesses the individual's degree of organization, dependability, and attention to detail."
    )
    extraversion: TraitScore = Field(
      ..., description="Captures the extent to which Person A seeks stimulation from social interactions and enjoys being in the company of others."
    )
    agreeableness: TraitScore = Field( description="Measures Person A's tendencies toward cooperation, trust, and empathy.")
    neuroticism: TraitScore = Field(
      ..., description="Indicates the degree to which Person A experiences emotional instability, anxiety, or moodiness.")

# 2. Character Traits

class CharacterTraits(BaseModel):
    honesty: TraitScore = Field(
      ..., description="Evaluates the extent to which Person A values truthfulness and transparency in their behavior and communication.")
    integrity: TraitScore = Field(
      ..., description="Assesses adherence to moral principles and ethical standards.")
    empathy: TraitScore = Field(
      ..., description="Measures Person A's capacity to understand and share the emotions of others.")
    loyalty: TraitScore = Field(
      ..., description="Assesses the degree of commitment Person A shows to maintaining supportive and dependable relationships.")
    courage: TraitScore = Field(
      ..., description="Evaluates Person A's ability to act in the face of fear or risk, especially when moral or ethical principles are at stake.")
    humility: TraitScore = Field(
      ..., description="Captures Person A's ability to recognize their limitations and maintain modesty in interactions.")

# 3. Cognitive Compatibility

class CognitiveCompatibility(BaseModel):
    communication_style: TraitScore = Field(
      ..., description="Evaluates the similarity between Person A’s communication style and that of the known character.")
    problem_solving_approach: TraitScore = Field(
      ..., description="Assesses the similarity in how Person A approaches solving problems compared to the known character.")
    emotional_intelligence: TraitScore = Field(
      ..., description="Measures the degree to which Person A and the known character are able to perceive, interpret, and manage emotions.")
    values_alignment: TraitScore = Field(
      ..., description="Evaluates the similarity in values (e.g., loyalty, justice, fairness) between Person A and the known character.")

class AnalysisResult(BaseModel):
    person_a_name: str
    known_character_name: str
    personality_traits: PersonalityTraits
    character_traits: CharacterTraits
    cognitive_compatibility: CognitiveCompatibility

# The Myers-Briggs Type Indicator (MBTI) is one of the most widely used personality typologies

class DichotomyScore(BaseModel):
    score: float = Field(
      ..., ge=0.0, le=100.0, description="Score represents the relative strength of each trait in the dichotomy.Score 0-33: Represents stronger tendencies for the second trait in the dichotomy (e.g., Introversion, Sensing, Feeling, Perceiving). Score 34-66: Indicates a balance or moderate preference for both traits. Score 67-100: Represents stronger tendencies for the first trait in the dichotomy (e.g., Extraversion, Intuition, Thinking, Judging)")
    justification: str = Field(
      ..., description="Provide a detailed justification for the score, citing specific behaviors observed during the interaction.")

class MBTITraits(BaseModel):
    extraversion_introversion: DichotomyScore = Field(
        ..., description="Measures whether Person A tends to focus on external events and social interactions (Extraversion) or prefers internal thoughts and solitary activities (Introversion)."
    )
    sensing_intuition: DichotomyScore = Field(
        ..., description="Assesses whether Person A focuses on concrete, factual information (Sensing) or abstract concepts and patterns (Intuition)."
    )
    thinking_feeling: DichotomyScore = Field(
        ..., description="Evaluates whether Person A tends to make decisions based on logic and objective analysis (Thinking) or based on emotions and interpersonal harmony (Feeling)."
    )
    judging_perceiving: DichotomyScore = Field(
        ..., description="Measures whether Person A prefers structure and planning (Judging) or a flexible, adaptable approach to life (Perceiving)."
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
