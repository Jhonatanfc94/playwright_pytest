
class UtilsChatbot:
    def validate_response(response, expected_response_array):
        if response is None or expected_response_array is None:
            raise ValueError("Response and expected_response_array cannot be None")
        
        if not isinstance(response, str) or response.strip() == "":
            return ValueError("Response cannot be empty or non-string")
        
        if not isinstance(expected_response_array, (list, tuple)):
            raise ValueError("Expected_response_array must be a list or tuple")
        
        if not expected_response_array:
            return ValueError("Expected_response_array cannot be empty")
        
        response_lower = response.lower()
        error_messages = []
        for expected in expected_response_array:
            if not isinstance(expected, str):
                continue
            if expected.lower() not in response_lower:
                error_messages.append(f"'{expected}' not found in response")

        if error_messages:
            return (False, " | ".join(error_messages))
        return (True, "All expected elements found in response")
