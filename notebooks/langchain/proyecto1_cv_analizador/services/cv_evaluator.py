from langchain_openai import ChatOpenAI
from models.cv_models import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts

import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("OPENAI_API_KEY"):
    print("cargado correctamente")


def crear_evaluador_cv():
    modelo_base = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )

    modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
    chat_prompt = crear_sistema_prompts()
    cadena_evaluacion = chat_prompt | modelo_estructurado
    
    return cadena_evaluacion

def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
    try:
        cadena_evaluacion = crear_evaluador_cv()

        resultado = cadena_evaluacion.invoke({
            "texto_cv": texto_cv,
            "descripcion_puesto": descripcion_puesto
        })
        print(resultado)
        return resultado
    except Exception as e:
        print(e)
        return AnalisisCV(
            nombre_candidato="Error en procesamiento.",
            experiencia_años=0,
            habilidades_clave=["error al procesar cv"],
            educacion="no se puede determinar",
            experiencia_relevante="Error durante el analisis",
            fortalezas=["Requiere revison manual del cv"],
            areas_mejora= ["Error al procesar cv"],
            porcentaje_ajuste=0           
        )


