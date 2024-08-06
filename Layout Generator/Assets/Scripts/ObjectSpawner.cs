using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using UnityEditor;

public class ObjectSpawner : MonoBehaviour
{
    public string csvFileName = "your_csv_file"; // Name of your CSV file without the extension
    public string parentObjectName = "ParentObject"; // Name of the parent object
    public string wallObjectName = "Wall"; // Name to identify wall objects
    public string windowObjectName = "Window"; // Name to identify window objects

    private GameObject parentObject;
    private List<string> objectReport = new List<string>();
    private List<Vector3> windowPositions = new List<Vector3>();
    private List<Vector3> windowSizes = new List<Vector3>();

    void Start()
    {
        // Find or create the parent object
        parentObject = GameObject.Find(parentObjectName);
        if (parentObject == null)
        {
            parentObject = new GameObject(parentObjectName);
        }

        LoadCSVAndSpawnObjects();
        GenerateReport();
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.P))
        {
            SaveParentObjectAsPrefab();
        }
    }

    void LoadCSVAndSpawnObjects()
    {
        string filePath = Path.Combine(Application.dataPath, "Resources", csvFileName + ".csv");

        if (File.Exists(filePath))
        {
            string[] csvLines = File.ReadAllLines(filePath);

            for (int i = 1; i < csvLines.Length; i++) // Start at 1 to skip header
            {
                string[] values = csvLines[i].Split(',');

                if (values.Length == 11)
                {
                    string objectName = values[0];
                    int id = int.Parse(values[1]);
                    float posX = float.Parse(values[2]);
                    float posY = float.Parse(values[3]);
                    float posZ = float.Parse(values[4]);
                    float rotX = float.Parse(values[5]);
                    float rotY = float.Parse(values[6]);
                    float rotZ = float.Parse(values[7]);
                    float sizeX = float.Parse(values[8]);
                    float sizeY = float.Parse(values[9]);
                    float sizeZ = float.Parse(values[10]);

                    Vector3 position = new Vector3(posX, posY, posZ);
                    Quaternion rotation = Quaternion.Euler(rotX, rotY, rotZ);
                    Vector3 size = new Vector3(sizeX, sizeY, sizeZ);

                    if (objectName == windowObjectName)
                    {
                        windowPositions.Add(position);
                        windowSizes.Add(size);
                    }
                    else
                    {
                        SpawnObject(objectName, id, position, rotation, size);
                    }
                }
                else
                {
                    Debug.LogWarning("CSV line does not have the correct number of values: " + csvLines[i]);
                }
            }
        }
        else
        {
            Debug.LogError("CSV file not found at path: " + filePath);
        }
    }

    void SpawnObject(string objectName, int id, Vector3 position, Quaternion rotation, Vector3 size)
    {
        GameObject prefab = Resources.Load<GameObject>(objectName);

        if (prefab == null && objectName != wallObjectName)
        {
            string reportLine = $"Object '{objectName}' is not on the scene and could not be found in the Resources folder.";
            Debug.Log($"INFO: {reportLine}");
            objectReport.Add(reportLine);
            return;
        }

        if (objectName == wallObjectName)
        {
            GenerateCubesForWall(id, position, rotation, size);
        }
        else
        {
            GameObject obj = Instantiate(prefab, position, rotation);
            obj.name = objectName + "_" + id;
            obj.transform.localScale = size;
            obj.transform.SetParent(parentObject.transform);

            string report = $"Object: {obj.name}, Position: {obj.transform.position}, Rotation: {obj.transform.rotation.eulerAngles}, Scale: {obj.transform.localScale}";
            objectReport.Add(report);
        }
    }

    void GenerateCubesForWall(int id, Vector3 position, Quaternion rotation, Vector3 size)
    {
        GameObject wallParent = new GameObject(wallObjectName + "_" + id);
        wallParent.transform.position = position;
        wallParent.transform.SetParent(parentObject.transform);

        float cubeSize = 0.5f;
        for (int x = 0; x < size.x * 2; x++)
        {
            for (int y = 0; y < size.y * 2; y++)
            {
                for (int z = 0; z < size.z * 2; z++)
                {
                    Vector3 cubePosition = position + new Vector3(x * cubeSize + 0.25f, y * cubeSize + 0.25f, z * cubeSize + 0.25f);

                    if (!IsPositionInWindow(cubePosition))
                    {
                        GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        cube.transform.position = cubePosition;
                        cube.transform.rotation = rotation;
                        cube.transform.localScale = new Vector3(cubeSize, cubeSize, cubeSize);
                        cube.transform.SetParent(wallParent.transform);
                    }
                }
            }
        }

        wallParent.transform.rotation = rotation;

        string report = $"Wall Object: {wallParent.name}, Position: {wallParent.transform.position}, Rotation: {wallParent.transform.rotation.eulerAngles}, Cubes generated: {size.x * size.y * size.z}";
        objectReport.Add(report);
    }

    bool IsPositionInWindow(Vector3 position)
    {
        for (int i = 0; i < windowPositions.Count; i++)
        {
            Vector3 windowPos = windowPositions[i];
            Vector3 windowSize = windowSizes[i];

            if (position.x >= windowPos.x && position.x <= windowPos.x + windowSize.x &&
                position.y >= windowPos.y && position.y <= windowPos.y + windowSize.y &&
                position.z >= windowPos.z && position.z <= windowPos.z + windowSize.z)
            {
                return true;
            }
        }
        return false;
    }

    void SaveParentObjectAsPrefab()
    {
#if UNITY_EDITOR
        string directoryPath = Path.Combine(Application.dataPath, "Resources", "Environments");
        if (!Directory.Exists(directoryPath))
        {
            Directory.CreateDirectory(directoryPath);
        }

        string prefabPath = Path.Combine(directoryPath, parentObjectName + ".prefab");
        PrefabUtility.SaveAsPrefabAsset(parentObject, prefabPath);
        Debug.Log("Parent object saved as prefab at: " + prefabPath);
#endif
    }

    void GenerateReport()
    {
        string reportFilePath = Path.Combine(Application.dataPath, "Resources", "object_report.txt");
        File.WriteAllLines(reportFilePath, objectReport);
        Debug.Log("Report generated at: " + reportFilePath);
    }
}
