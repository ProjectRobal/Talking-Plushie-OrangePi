'''

 A script that converts text dataset into vectors which is then stored into Qdrant database used for RAG.
 
 An input dataset is stored in text file where each line is separated by newline characters.

'''
from fastembed import TextEmbedding
from timeit import default_timer as timer

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct


def main():
    
    input_filename:str = "texts.txt"
    server_address:str = "http://localhost:6333"
    
    model = TextEmbedding(model_name="mixedbread-ai/mxbai-embed-large-v1")
    
    qdrant = QdrantClient(server_address)
        
    # if qdrant.collection_exists(collection_name="ia"):
    #     init_from = InitFrom(collection="ia")
    
        
    qdrant.recreate_collection(
    collection_name="ia",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
        
    start = timer()
    
    points = []
    
    with open(input_filename,"r") as dataset:
        
        for id,text in enumerate(dataset.readlines()):
            points.append(
                PointStruct(
                    id=id,
                    vector=next(model.embed(text)),
                    payload={"text":text}
                )
            )
            
    qdrant.upsert(
        collection_name="ia",
        wait=True,
        points=points
    )
              
    end = timer()
    
    print("Processing time: ",end-start," s")
    
    query_text="Where do you come from?"
    
    query_vector=next(model.embed(query_text))
    
    search_result = qdrant.search(
    collection_name="ia",
    query_vector=query_vector,
    limit=5
    )
    print(search_result)

if __name__ == "__main__":
    main()