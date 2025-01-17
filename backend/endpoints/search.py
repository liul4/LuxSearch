from flask import Blueprint, jsonify, request
from dummy.data import dummyResponse
from config import USE_MOCK_DATA, RANK_SCORE
from utils.elasticsearch import elastic_client

search = Blueprint(name='search', import_name=__name__)

@search.route('/', methods=['GET'])
def search_query():
    if USE_MOCK_DATA:
        output = dummyResponse
        return jsonify(output)

    query = request.args.get('q')
    start = request.args.get('start', 0)
    query_body = {
        "from": start,
        "size": 10,
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "body": query
                    }
                },
                "functions": [
                {
                    "filter": {
                        "term": {
                            "relevance": 1
                        }
                    },
                    "weight": 2
                },
                {
                    "filter": {
                        "term": {
                            "relevance": 0
                        }
                    },
                        "weight": 1
                },
                {
                    "field_value_factor": {
                        "field": "likes",
                        "factor": RANK_SCORE['likes'],
                        "modifier": "log1p",
                        "missing": 1
                    }
                },
                {
                    "field_value_factor": {
                        "field": "retweets",
                        "factor": RANK_SCORE['retweets'],
                        "modifier": "log1p",
                        "missing": 1
                    }
                },
                {
                    "field_value_factor": {
                        "field": "upvotes",
                        "factor": RANK_SCORE['upvotes'],
                        "modifier": "log1p",
                        "missing": 1
                    }
                },
                {
                    "field_value_factor": {
                        "field": "comments",
                        "factor": RANK_SCORE['comments'],
                        "modifier": "log1p",
                        "missing": 1
                    }
                }
            ],
                "score_mode": "sum",
                "boost_mode": "sum"
            }
        }
    }


    res = elastic_client.search(index="twitter,reddit", body=query_body)
    return jsonify(res)