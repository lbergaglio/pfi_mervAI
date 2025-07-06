from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Modelo público y funcional (en español no hay uno perfecto, pero t5-base funciona para pruebas)
MODEL_NAME = "t5-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def adaptar_texto(texto_original, nivel):
    """
    Adapta un texto financiero para público general, explicando conceptos y evitando tecnicismos.
    El nivel puede usarse para ajustar el grado de explicación (no implementado en prompt, pero reservado).
    """
    prompt = (
        f"Reescribí y explicá el siguiente texto en varios párrafos, desarrollando cada punto y concepto financiero de manera sencilla y clara, para que cualquier persona sin conocimientos en finanzas pueda entenderlo. El texto adaptado debe ser lo más completo, extenso y detallado posible, cubriendo todos los aspectos de la noticia y agregando explicaciones o ejemplos simples cuando sea necesario. No omitas información relevante, no repitas frases ni cortes el sentido. No inventes datos. Texto original:\n{texto_original}"
    )
    # Para t5-base, anteponer 'summarize: ' ayuda a la generación
    prompt = "summarize: " + prompt
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=800,
            num_beams=4,
            early_stopping=True,
            length_penalty=1.3
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
