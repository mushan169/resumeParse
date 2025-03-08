class Response:
    SUCCESS_CODE = 200
    FAIL_CODE = 500

    def __init__(self, code: int, message: str, data: any = None):
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        return {
            "code": self.status,
            "message": self.message,
            "data": self.data
        }

    @staticmethod
    def success(data: any = None, message: str = "success"):
        return Response(Response.SUCCESS_CODE, message, data)

    @staticmethod
    def fail(data: any = None, message: str = "fail"):
        return Response(Response.FAIL_CODE, message, data)
