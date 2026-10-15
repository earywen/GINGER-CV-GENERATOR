# -*- coding: utf-8 -*-
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class CVReference(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(description="Titre du projet / client / site en MAJUSCULES")
    tag: str = Field(description="Badge thématique court (2 à 4 mots en MAJUSCULES)")
    desc: str = Field(description="Synthèse claire et factuelle de 18 à 28 mots")

class CVDataModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Prénom NOM du collaborateur")
    trigram: str = Field(default="", description="Trigramme officiel Burgeap (3-4 lettres)")
    initials: str = Field(default="", description="Initiales officielles (ex: MR, JGR)")

    role_fr: str = Field(description="Intitulé exact du poste en Français")
    role_en: str = Field(description="Official job title in English")

    exp_fr: str = Field(description="Années d'expérience en Français (ex: '8 ans d'expérience')")
    exp_en: str = Field(description="Years of experience in English (ex: '8 years of experience')")

    agency_fr: str = Field(description="Direction régionale ou agence en Français")
    agency_en: str = Field(description="Regional directorate or office in English")

    formations_fr: List[str] = Field(default_factory=list, description="Diplômes et formations en Français")
    formations_en: List[str] = Field(default_factory=list, description="Degrees and training in English")

    competences_fr: List[str] = Field(default_factory=list, description="Compétences clés en Français")
    competences_en: List[str] = Field(default_factory=list, description="Core competencies in English")

    exp_pros_fr: List[str] = Field(default_factory=list, description="Parcours chez les véritables employeurs en Français")
    exp_pros_en: List[str] = Field(default_factory=list, description="Career path with actual employers in English")

    langs_fr: List[str] = Field(default_factory=list, description="Langues et mobilité en Français")
    langs_en: List[str] = Field(default_factory=list, description="Languages and mobility in English")

    pitch_fr: str = Field(description="Synthèse de parcours valorisante d'environ 45-55 mots en Français")
    pitch_en: str = Field(description="Executive profile summary of 45-55 words in English")

    qualifs_fr: List[str] = Field(default_factory=list, description="4 qualifications clés réelles en Français")
    qualifs_en: List[str] = Field(default_factory=list, description="4 core qualifications in English")

    refs_fr: List[CVReference] = Field(default_factory=list, description="Missions et projets de référence en Français")
    refs_en: List[CVReference] = Field(default_factory=list, description="Key project references in English")

    # Optional metadata or UI overrides
    photo_b64: Optional[str] = None
    t_formations_fr: Optional[str] = None
    t_formations_en: Optional[str] = None
    t_competences_fr: Optional[str] = None
    t_competences_en: Optional[str] = None

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
