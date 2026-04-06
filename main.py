import sys
import uvicorn
from backend.logger import log_header, log_info, log_success, log_error
from backend.doc_ingestion import ingest_documents


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "ingest":
        log_header("Ingesting LangChain Documents")
        ingest_documents()
        log_success("Done!")

    elif command == "serve":
        log_header("Starting LangChain Doc Helper Server")
        log_info("Backend: http://localhost:8000")
        log_info("API Docs: http://localhost:8000/docs")
        log_info("Frontend: Run 'cd frontend && npm run dev' separately")
        uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)

    elif command == "help" or command == "--help" or command == "-h":
        print_usage()

    else:
        log_error(f"Unknown command: {command}")
        print_usage()


def print_usage():
    print("\nUsage: python main.py <command>\n")
    print("Commands:")
    print("  ingest    Crawl and index LangChain documents to Pinecone")
    print("  serve     Start the FastAPI backend server")
    print("  help      Show this help message")
    print()


if __name__ == "__main__":
    main()
