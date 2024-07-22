using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using UnityEditor;

public class ObjectSpawner : MonoBehaviour
{
    public string csvFileName = "your_csv_file"; // Name of your CSV file without the extension
    public string parentObjectName = "ParentObject"; // Name of the parent object

    private GameObject parentObject;
    private List<string> objectReport = new List<string>();

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

                    SpawnObject(objectName, id, position, rotation, size);
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

        if (prefab == null)
        {
            string reportLine = $"Object '{objectName}' is not on the scene and could not be found in the Resources folder.";
            Debug.Log($"INFO: {reportLine}");
            objectReport.Add(reportLine);
            return;
        }

        GameObject obj = Instantiate(prefab, position, rotation);
        obj.name = objectName + "_" + id;
        obj.transform.localScale = size;
        obj.transform.SetParent(parentObject.transform);

        string report = $"Object: {obj.name}, Position: {obj.transform.position}, Rotation: {obj.transform.rotation.eulerAngles}, Scale: {obj.transform.localScale}";
        objectReport.Add(report);
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
