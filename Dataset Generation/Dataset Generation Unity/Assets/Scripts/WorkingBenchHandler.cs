using UnityEngine;

public class WorkingBenchHandler : MonoBehaviour
{
    public GameObject chairPrefab;   // Chair prefab
    public GameObject monitorPrefab; // Monitor prefab
    public GameObject laptopPrefab;  // Laptop prefab
    public GameObject controlPrefab;  // Control prefab
    public Transform parentObject;   // Parent object to attach generated objects as children

    void Start()
    {
        SpawnChairs();
        SpawnElectronics();
        ReleaseChildrenAndDestroy();
    }

    void SpawnChairs()
    {
        // Randomly decide to spawn 0, 1, or 2 chairs
        int chairCount = Random.Range(0, 3);

        if (chairCount == 1)
        {
            float x = Random.Range(-0.5f, 0.5f);
            float z = Random.Range(-0.8f, -0.65f);
            Vector3 localPosition = new Vector3(x, 0, z);

            GameObject chair = Instantiate(chairPrefab, parentObject);
            chair.transform.localPosition = localPosition;
        }
        else if (chairCount == 2)
        {
            // Two chairs positioned symmetrically
            float x1 = Random.Range(0.3f, 0.5f);
            float x2 = -x1;
            float z = Random.Range(-0.8f, -0.65f);

            Vector3 localPosition1 = new Vector3(x1, 0, z);
            Vector3 localPosition2 = new Vector3(x2, 0, z);

            GameObject chair1 = Instantiate(chairPrefab, parentObject);
            chair1.transform.localPosition = localPosition1;

            GameObject chair2 = Instantiate(chairPrefab, parentObject);
            chair2.transform.localPosition = localPosition2;
        }
    }

    void SpawnElectronics()
    {
        // Randomly choose the number of electronics (1 or 2)
        int electronicsCount = Random.Range(1, 3);

        // Set the rotation with a y-axis rotation of -180
        Quaternion rotation = Quaternion.Euler(0, -180, 0);

        // Helper function to get a random electronic prefab
        GameObject GetRandomElectronicPrefab()
        {
            int choice = Random.Range(0, 3); // 0 = laptop, 1 = monitor, 2 = chair
            switch (choice)
            {
                case 0: return laptopPrefab;
                case 1: return monitorPrefab;
                case 2: return controlPrefab;
                default: return laptopPrefab; // Fallback
            }
        }

        if (electronicsCount == 1)
        {
            float x = Random.Range(-0.65f, 0.65f);
            float z = Random.Range(-0.15f, 0.15f);
            Vector3 localPosition = new Vector3(x, 0.712f, z);

            GameObject electronic = Instantiate(GetRandomElectronicPrefab(), parentObject);
            electronic.transform.localPosition = localPosition;
            electronic.transform.localRotation = rotation;
        }
        else
        {
            float x1 = Random.Range(0.2f, 0.65f);
            float x2 = -x1;
            float z1 = Random.Range(-0.15f, 0.15f);
            float z2 = Random.Range(-0.15f, 0.15f);

            Vector3 localPosition1 = new Vector3(x1, 0.712f, z1);
            Vector3 localPosition2 = new Vector3(x2, 0.712f, z2);

            GameObject electronic1 = Instantiate(GetRandomElectronicPrefab(), parentObject);
            electronic1.transform.localPosition = localPosition1;
            electronic1.transform.localRotation = rotation;

            GameObject electronic2 = Instantiate(GetRandomElectronicPrefab(), parentObject);
            electronic2.transform.localPosition = localPosition2;
            electronic2.transform.localRotation = rotation;
        }
    }

    void ReleaseChildrenAndDestroy()
    {
        while (parentObject.childCount > 0)
        {
            Transform child = parentObject.GetChild(0);
            child.SetParent(null);
        }

        Destroy(gameObject);
    }
}
