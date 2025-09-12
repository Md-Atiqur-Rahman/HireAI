from sentence_transformers import SentenceTransformer, util


def calculate_semantic_similarity(text1, text2):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
    return float(similarity_score[0][0]) * 100