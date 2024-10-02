from kubernetes import client, config

def list_pods():
    # Load the in-cluster configuration
    config.load_incluster_config()

    # Initialize the CoreV1Api
    v1 = client.CoreV1Api()

    # List all pods in all namespaces
    pods = v1.list_pod_for_all_namespaces(watch=False)
    
    for pod in pods.items:
        print(f"Namespace: {pod.metadata.namespace}, Pod Name: {pod.metadata.name}")

if __name__ == '__main__':
    list_pods()