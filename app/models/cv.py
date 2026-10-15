# -*- coding: utf-8 -*-
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class CVReference(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(description="Titre du projet / client / site en MAJUSCULES")
    tag: str = Field(description="Badge thématique court (2 à 4 mots en MAJUSCULES)")
    desc: str = Field(description="Synthèse claire et factuelle de 18 à 28 mots")

class CVExtractionSchema(BaseModel):
    """Schema strictly enforced for AI parsing."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Prénom NOM du collaborateur")
    trigram: str = Field(description="Trigramme officiel Burgeap (3-4 lettres)")
    initials: str = Field(description="Initiales officielles (ex: MR, JGR)")

    role_fr: str = Field(description="Intitulé exact du poste en Français")
    role_en: str = Field(description="Official job title in English")

    exp_fr: str = Field(description="Années d'expérience et ancienneté en Français (ex: '6 ans d\\'expérience, dont 3 ans chez GINGER BURGEAP')")
    exp_en: str = Field(description="Years of experience and tenure in English (ex: '6 years of experience, including 3 years at GINGER BURGEAP')")

    agency_fr: str = Field(description="Direction régionale ou agence en Français")
    agency_en: str = Field(description="Regional directorate or office in English")

    diplomes_fr: List[str] = Field(default_factory=list, description="Diplômes académiques de l'enseignement supérieur en Français (ex: '2018 : Master 2 Géologie...')")
    diplomes_en: List[str] = Field(default_factory=list, description="Higher education academic degrees in English (ex: '2018: Master\\'s Degree in Geology...')")

    formations_fr: List[str] = Field(default_factory=list, description="Formations professionnelles continues, habilitations sécurité et certifications en Français (ex: 'Habilitation SST', 'AIPR Concepteur', 'CATEC')")
    formations_en: List[str] = Field(default_factory=list, description="Professional training, safety accreditations and certifications in English (ex: 'SST First Aid Certification', 'AIPR Accreditation')")

    competences_fr: List[str] = Field(description="Compétences clés en Français")
    competences_en: List[str] = Field(description="Core competencies in English")

    exp_pros_fr: List[str] = Field(description="Parcours chez les véritables employeurs en Français")
    exp_pros_en: List[str] = Field(description="Career path with actual employers in English")

    langs_fr: List[str] = Field(description="Langues et mobilité en Français")
    langs_en: List[str] = Field(description="Languages and mobility in English")

    pitch_fr: str = Field(description="Synthèse de parcours valorisante d'environ 45-55 mots en Français")
    pitch_en: str = Field(description="Executive profile summary of 45-55 words in English")

    qualifs_fr: List[str] = Field(description="4 qualifications clés réelles en Français")
    qualifs_en: List[str] = Field(description="4 core qualifications in English")

    refs_fr: List[CVReference] = Field(description="Missions et projets de référence en Français")
    refs_en: List[CVReference] = Field(description="Key project references in English")

class CVDataModel(CVExtractionSchema):
    """Full CV model including optional UI metadata and photo."""
    model_config = ConfigDict(extra="allow")

    photo_b64: Optional[str] = None
    t_diplomes_fr: Optional[str] = None
    t_diplomes_en: Optional[str] = None
    t_formations_fr: Optional[str] = None
    t_formations_en: Optional[str] = None
    t_competences_fr: Optional[str] = None
    t_competences_en: Optional[str] = None
    show_badges: bool = True

def get_cv_extraction_json_schema() -> Dict[str, Any]:
    """Generates the clean JSON schema used for agy CLI structured output."""
    return CVExtractionSchema.model_json_schema()

class RenderPayload(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict, description="Données complètes structurées du CV")
    lang: str = Field(default="fr", description="Code langue ('fr' ou 'en')")

class CropPhotoResponse(BaseModel):
    status: str
    photo_b64: str

class ParseJobResponse(BaseModel):
    status: str
    job_id: str

class JobStatusResponse(BaseModel):
    status: str
    progress: int
    step: str
    desc: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float
