from app.core.db import dynamodb

USER_MOVIES_TABLE = "UserMovies"
USER_SERIES_TABLE = "UserSeries"
MOVIES_TABLE = "movies"
SERIES_TABLE = "TVSeries"

class FavoritesRepository:
    @staticmethod
    def get_imdb_id_from_title(title: str, table_name: str):
        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression="Title = :title",
            ExpressionAttributeValues={":title": {"S": title}}
        )
        items = response.get("Items", [])
        if not items:
            return None
        return items[0]["imdbID"]["S"]

    @staticmethod
    def get_favorite_movies(email: str):
        response = dynamodb.query(
            TableName=USER_MOVIES_TABLE,
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": {"S": email}}
        )
        items = response.get("Items", [])
        result = []
        for m in items:
            try:
                result.append({
                    "Title": m.get("Title", {}).get("S", "Unknown"),
                    "imdbID": m.get("imdbID", {}).get("S", "Unknown")
                })
            except Exception as e:
                print(f"Error processing item: {m}, Error: {e}")
        return result

    @staticmethod
    def get_favorite_series(email: str):
        response = dynamodb.query(
            TableName=USER_SERIES_TABLE,
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": {"S": email}}
        )
        return [{"Title": s["Title"]["S"], "imdbID": s["imdbID"]["S"]} for s in response.get("Items", [])]

    @staticmethod
    def add_favorite_movie(email: str, title: str, imdb_id: str = None):
        
        if imdb_id:
            dynamodb.put_item(
                TableName=USER_MOVIES_TABLE,
                Item={"email": {"S": email}, "imdbID": {"S": imdb_id}, "Title": {"S": title}}
            )
            return {"message": f"Movie '{title}' added to favorites!"}
        
        # Otherwise, try to find it in movies table
        imdb_id = FavoritesRepository.get_imdb_id_from_title(title, MOVIES_TABLE)
        if not imdb_id:
            return {"error": f"Movie '{title}' not found!"}

        dynamodb.put_item(
            TableName=USER_MOVIES_TABLE,
            Item={"email": {"S": email}, "imdbID": {"S": imdb_id}, "Title": {"S": title}}
        )
        return {"message": f"Movie '{title}' added to favorites!"}

    @staticmethod
    def add_favorite_series(email: str, title: str, imdb_id: str = None):
        # If imdb_id is provided, use it directly
        if imdb_id:
            dynamodb.put_item(
                TableName=USER_SERIES_TABLE,
                Item={"email": {"S": email}, "imdbID": {"S": imdb_id}, "Title": {"S": title}}
            )
            return {"message": f"Series '{title}' added to favorites!"}
        
        # Otherwise, try to find it in series table
        imdb_id = FavoritesRepository.get_imdb_id_from_title(title, SERIES_TABLE)
        if not imdb_id:
            return {"error": f"Series '{title}' not found!"}

        dynamodb.put_item(
            TableName=USER_SERIES_TABLE,
            Item={"email": {"S": email}, "imdbID": {"S": imdb_id}, "Title": {"S": title}}
        )
        return {"message": f"Series '{title}' added to favorites!"}

    @staticmethod
    def delete_favorite_movie(email: str, title: str):
        response = dynamodb.scan(
            TableName=USER_MOVIES_TABLE,
            FilterExpression="email = :email AND Title = :title",
            ExpressionAttributeValues={":email": {"S": email}, ":title": {"S": title}}
        )
        items = response.get("Items", [])
        if not items:
            return {"error": f"Movie '{title}' not found in favorites!"}

        imdb_id = items[0]["imdbID"]["S"]

        dynamodb.delete_item(
            TableName=USER_MOVIES_TABLE,
            Key={"email": {"S": email}, "imdbID": {"S": imdb_id}}
        )
        return {"message": f"Movie '{title}' removed from favorites!"}

    @staticmethod
    def delete_favorite_series(email: str, title: str):
        response = dynamodb.scan(
            TableName=USER_SERIES_TABLE,
            FilterExpression="email = :email AND Title = :title",
            ExpressionAttributeValues={":email": {"S": email}, ":title": {"S": title}}
        )
        items = response.get("Items", [])
        if not items:
            return {"error": f"Series '{title}' not found in favorites!"}

        imdb_id = items[0]["imdbID"]["S"]

        dynamodb.delete_item(
            TableName=USER_SERIES_TABLE,
            Key={"email": {"S": email}, "imdbID": {"S": imdb_id}}
        )
        return {"message": f"Series '{title}' removed from favorites!"}
