from logger import logger


class Iteration(object):
    
    def __init__(self, initial_query, validation_callback=None):
        self.initial_query = initial_query
        self.log = []
        self.validation_callback = validation_callback


    def validate(self, result):
        if self.validation_callback:
            return_code, return_message = self.validation_callback(result)
            return return_code, return_message 
        
        return 0, ""
    
    def run(self, llm_client):
        done = False
        feedback = ""
        return_message = ""
        while not done:
            query = f"{self.initial_query}"
            if len(self.log):
                query += "\n".join(self.log)
            
            result = llm_client.send_message(query)
            return_code, return_message = self.validate(result)
            logger.info("#"*50)
            logger.info(f"LLM request: {query}")
            logger.info(f"LLM response: {result}")
            logger.info("#"*50)
            logger.info(f"Return code: {return_code}")
            logger.info(f"Return message: {return_message}")
            feedback = self.ask_feedback()
            if return_message:
                self.log.append(f"Error: {return_message}")
            if feedback:    
                self.log.append(f"Recomendations: {feedback}")

            done = (return_code == 0) and (not feedback)
        
        return return_message


    def ask_feedback(self):
        return input("What would You think about this iteration: ")


class FakeIteration(object):

    def __init__(self, fake_response):
        self.fake_response = fake_response
    
    def run(self, *args, **kwargs):
        return self.fake_response
