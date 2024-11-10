using UnityEngine;

public class WorkingBenchHandler : MonoBehaviour
{
    public GameObject chairPrefab;   // Chair prefab
    public GameObject monitorPrefab; // Monitor prefab
    public GameObject laptopPrefab;  // Laptop prefab
    public Transform parentObject;   // Parent object to attach generated objects as children

    void Start()
    {
        SpawnChairs();
        SpawnElectronics();
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
        // Randomly choose the number and type of electronics
        int electronicsCount = Random.Range(1, 3); // Either 1 or 2 objects
        bool isLaptop1 = Random.Range(0, 2) == 0;
        bool isLaptop2 = Random.Range(0, 2) == 0;

        // Set the rotation with a y-axis rotation of -180
        Quaternion rotation = Quaternion.Euler(0, -180, 0);

        // Single electronic device case
        if (electronicsCount == 1)
        {
            float x = Random.Range(-0.65f, 0.65f);
            float z = Random.Range(-0.15f, 0.15f);
            Vector3 localPosition = new Vector3(x, 0.712f, z);

            GameObject electronic = Instantiate(isLaptop1 ? laptopPrefab : monitorPrefab, parentObject);
            electronic.transform.localPosition = localPosition;
            electronic.transform.localRotation = rotation;
        }
        else // Two electronic devices case
        {
            float x1 = Random.Range(0.2f, 0.65f);
            float x2 = -x1;
            float z1 = Random.Range(-0.15f, 0.15f);
            float z2 = Random.Range(-0.15f, 0.15f);

            Vector3 localPosition1 = new Vector3(x1, 0.712f, z1);
            Vector3 localPosition2 = new Vector3(x2, 0.712f, z2);

            // Instantiate first electronic device
            GameObject electronic1 = Instantiate(isLaptop1 ? laptopPrefab : monitorPrefab, parentObject);
            electronic1.transform.localPosition = localPosition1;
            electronic1.transform.localRotation = rotation;

            // Instantiate second electronic device
            GameObject electronic2 = Instantiate(isLaptop2 ? laptopPrefab : monitorPrefab, parentObject);
            electronic2.transform.localPosition = localPosition2;
            electronic2.transform.localRotation = rotation;
        }
    }
}
