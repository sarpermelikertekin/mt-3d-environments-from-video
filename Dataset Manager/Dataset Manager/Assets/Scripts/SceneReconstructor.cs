using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class SceneReconstructor : MonoBehaviour
{
    [Tooltip("Prefab for walls")]
    public GameObject wallPrefab;

    [Tooltip("Prefab for chairs")]
    public GameObject chairPrefab;

    [Tooltip("Primitive type for other objects")]
    public PrimitiveType primitiveType = PrimitiveType.Cube;

    [Tooltip("File number of the CSV file to load")]
    public int fileNumber = 0;

    [Tooltip("File number of the CSV file to load")]
    public string datasetName;

    private string baseDirectory = @"";
    private string dataSetDirectory = "";

    private GameObject reconstructedRoomParent; // Parent object for reconstructed scene

    void Start()
    {
        dataSetDirectory = Path.Combine(baseDirectory, datasetName, "scene_meta");
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.R))
        {
            // Load and spawn objects from the selected CSV file
            string filePath = Path.Combine(dataSetDirectory, $"{fileNumber}.csv");

            if (File.Exists(filePath))
            {
                // If a previous reconstructed room exists, delete it
                if (reconstructedRoomParent != null)
                {
                    Destroy(reconstructedRoomParent);
                }

                // Create a new parent object for the room
                reconstructedRoomParent = new GameObject("GeneratedRoom");

                // Spawn objects from the CSV file
                SpawnObjectsFromCSV(filePath);
            }
            else
            {
                Debug.LogError($"File not found: {filePath}");
            }
        }
    }

    void SpawnObjectsFromCSV(string filePath)
    {
        // Read all lines from the CSV file
        string[] lines = File.ReadAllLines(filePath);

        // Iterate over each line (each line represents an object)
        foreach (string line in lines)
        {
            string[] data = line.Split(',');

            if (data.Length < 11) // Check if there's enough data in the row (name, position, rotation, scale)
            {
                Debug.LogWarning("Invalid data row in CSV file.");
                continue;
            }

            // Extract object information from the row
            string objectName = data[0];
            Vector3 position = new Vector3(float.Parse(data[1]), float.Parse(data[2]), float.Parse(data[3]));
            Quaternion rotation = new Quaternion(float.Parse(data[4]), float.Parse(data[5]), float.Parse(data[6]), float.Parse(data[7]));
            Vector3 scale = new Vector3(float.Parse(data[8]), float.Parse(data[9]), float.Parse(data[10]));

            // Decide which object to spawn based on the name
            GameObject spawnedObject = null;

            if (objectName.ToLower().Contains("wall"))
            {
                // Instantiate from the wall prefab
                spawnedObject = Instantiate(wallPrefab, position, rotation);
            }
            else if (objectName.ToLower().Contains("chair"))
            {
                // Instantiate from the chair prefab
                spawnedObject = Instantiate(chairPrefab, position, rotation);
            }
            else if (objectName.ToLower().Contains("plane"))
            {
                // Instantiate a plane for floors or ceilings
                spawnedObject = GameObject.CreatePrimitive(PrimitiveType.Plane);
                spawnedObject.transform.position = position;
                spawnedObject.transform.rotation = rotation;
            }
            else if (objectName.ToLower().Contains("point light"))
            {
                // Instantiate a point light
                GameObject lightGameObject = new GameObject("Point Light");
                Light pointLight = lightGameObject.AddComponent<Light>();
                pointLight.type = LightType.Point;
                lightGameObject.transform.position = position;
                lightGameObject.transform.rotation = rotation;
                lightGameObject.transform.localScale = scale;
                lightGameObject.transform.parent = reconstructedRoomParent.transform; // Parent to Reconstructed Room
                continue; // Skip the rest since point lights don't need scaling or other primitive settings
            }
            else if (objectName.ToLower().Contains("camera"))
            {
                // Find the main camera and update its transform
                Camera mainCamera = Camera.main;
                if (mainCamera != null)
                {
                    mainCamera.transform.position = position;
                    mainCamera.transform.rotation = rotation;
                    mainCamera.transform.localScale = scale;
                    Debug.Log("Main camera transform updated.");
                }
                else
                {
                    Debug.LogError("Main camera not found.");
                }
                continue; // Skip adding the camera to the parent object
            }
            else
            {
                // Instantiate a primitive object for other objects
                spawnedObject = GameObject.CreatePrimitive(primitiveType);
                spawnedObject.transform.position = position;
                spawnedObject.transform.rotation = rotation;
            }

            if (spawnedObject != null)
            {
                // Apply the scale
                spawnedObject.transform.localScale = scale;

                // Set the parent to the "Reconstructed Room" GameObject
                spawnedObject.transform.parent = reconstructedRoomParent.transform;

                Debug.Log($"Spawned {objectName} at {position} with rotation {rotation} and scale {scale}");
            }
        }
    }
}
