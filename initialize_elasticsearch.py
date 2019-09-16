from src.utils.elasticsearch_utils import ElasticSearchUtils

if __name__ == "__main__":
    ElasticSearchUtils.remove_index()
    ElasticSearchUtils.create_index()
