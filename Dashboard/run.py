from myapp import get_app
from waitress import serve

if __name__ == "__main__":
    print('Starting LayBack Dashboard App', flush=True)
    app = get_app()
    port = 8080
    print(f'Running on port {port}', flush=True)
    serve(app, host='0.0.0.0', port=port)
    print('Ending LayBack Dashboard App', flush=True)

"""
TODO: 
* Can't place an order that crosses the book? Or can, and it clicks?

"""