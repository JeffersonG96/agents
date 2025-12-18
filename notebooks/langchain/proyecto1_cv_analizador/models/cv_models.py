from pydantic import BaseModel, Field

class AnalisisCV(BaseModel):
    """Modelo de datos para el análisis completo de un CV"""
    nombre_candidato: str = Field(description="Nombre completo del cantidato extraido del documento")
    experiencia_años: int = Field(description="Años de experiencia laboral relevante")
    habilidades_clave: list[str] = Field(description="lista de las 5 a 7 habilidades delm candidato mas relevantes")
    educacion: str = Field(description="Nivel de educacion mas alto y especilazacion principal del candidato")
    experiencia_relevante: str = Field(description="Resumen conciso de la experiencia más relavante para el puesto específico")
    fortalezas: list[str] = Field(description="De 3 a 5 fortalezas del candidato basado en su perfil")
    areas_mejora: list[str] = Field(description="De 2 a 4 áreas donde el candidato podría desempeñar mejor")
    porcentaje_ajuste: int = Field(description="Porcentaje de ajuste al puesto de 0 a 100 basado en la experiencia, habilidades y formacion",ge=0,le=100)