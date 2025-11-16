# Importações necessárias
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

import difflib  # Importa a biblioteca nativa de Diff
import Levenshtein # Importa a biblioteca Levenshtein

# --- Modelos ---
# 1. Inicializa o FastAPI
app = FastAPI()

origins = [
    "http://localhost:4200",  # Permite o endereço padrão do Angular
    "http://127.0.0.1:4200", # Outra forma de localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Carrega o modelo BERT (sentence-transformer)
#    Isso é feito uma vez quando a API inicia, não a cada requisição.
#    'all-MiniLM-L6-v2' é um modelo excelente, rápido e leve.
print("Carregando modelo BERT...")
bert_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modelo BERT carregado.")

# 3. Define o "formato" dos dados que o frontend vai enviar (JSON)
class TextRequest(BaseModel):
    text1: str
    text2: str

# --- Lógica de Comparação ---

def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    """Calcula a similaridade usando TF-IDF e Cosseno."""
    # Cria o vetorizador TF-IDF
    vectorizer = TfidfVectorizer()
    
    # Lista de textos para comparar
    documents = [text1, text2]
    
    # Calcula a matriz TF-IDF
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calcula a similaridade de cossenos entre o doc 0 e o doc 1
    # O resultado é uma matriz, pegamos o valor [0, 1]
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Converte de numpy.float64 para float nativo do Python
    return float(similarity_matrix[0, 1]) 

def calculate_bert_similarity(text1: str, text2: str) -> float:
    """Calcula a similaridade semântica usando BERT (Sentence-BERT)."""
    # Lista de textos para codificar
    documents = [text1, text2]
    
    # Codifica os textos para vetores (embeddings)
    embeddings = bert_model.encode(documents)
    
    # Calcula a similaridade de cossenos entre os dois vetores
    # embeddings[0].reshape(1, -1) é necessário para cosine_similarity do scikit-learn
    similarity_matrix = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )
    
    # Pega o valor [0, 0] da matriz resultante
    return float(similarity_matrix[0, 0])

# --- NOVAS FUNÇÕES DE SIMILARIDADE (Rápidas) ---

def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Calcula a similaridade Jaccard (sobreposição de vocabulário)."""
    # Pega o conjunto (palavras únicas) de cada texto
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    
    if not set1 and not set2:
        return 1.0 # Dois conjuntos vazios são 100% similares
    if not set1 or not set2:
        return 0.0 # Um vazio e outro não, são 0% similares

    # Jaccard = (Interseção) / (União)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    return len(intersection) / len(union)

def calculate_levenshtein_ratio(text1: str, text2: str) -> float:
    """Calcula a "similaridade" baseada na distância de Levenshtein."""
    # Levenshtein.ratio() já retorna um score de 0.0 a 1.0 
    # (1.0 = idênticos)
    return Levenshtein.ratio(text1, text2)

# --- O Endpoint da API ---

@app.post("/compare")
async def compare_texts(request: TextRequest):
    """
    Recebe dois textos e retorna um DASHBOARD de 4 scores
    de similaridade.
    """
    text1 = request.text1
    text2 = request.text2

    # 1. Similaridade Semântica (IA)
    bert_score = calculate_bert_similarity(text1, text2)
    
    # 2. Similaridade de Palavras-Chave (Estatística)
    tfidf_score = calculate_tfidf_similarity(text1, text2)
    
    # 3. Similaridade de Vocabulário (Conjuntos)
    jaccard_score = calculate_jaccard_similarity(text1, text2)
    
    # 4. Similaridade Sintática (Typos/Edição)
    levenshtein_score = calculate_levenshtein_ratio(text1, text2)
    
    return {
        "bert_similarity (Semântica)": bert_score,
        "tfidf_similarity (Keywords)": tfidf_score,
        "jaccard_similarity (Vocabulário)": jaccard_score,
        "levenshtein_similarity (Estrutura/Typos)": levenshtein_score
    }

# Rota de "health check" para ver se a API está no ar
@app.get("/")
def read_root():
    return {"status": "API de Comparação de Textos está online!"}