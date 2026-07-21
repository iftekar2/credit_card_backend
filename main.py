from component.answer_question import query_documents, generate_response


def main():
    question = "How many points are offered for this credit card?"
    relevant_chunks = query_documents(question)
    answer = generate_response(question, relevant_chunks)
    print(answer)

if __name__ == "__main__": 
    main()