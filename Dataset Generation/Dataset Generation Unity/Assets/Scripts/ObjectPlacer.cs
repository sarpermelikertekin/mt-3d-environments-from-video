using UnityEngine;
using System.Collections.Generic;

public class ObjectPlacer : MonoBehaviour
{
    [Header("CSV Files")]
    public TextAsset objectCsvFile; // CSV file for object placement
    public TextAsset roomCsvFile; // CSV file for room dimensions

    [Header("Prefabs")]
    public List<GameObject> objectPrefabs; // Assign prefabs for each ID in order

    [Header("Camera Settings")]
    public Vector3 cameraPosition; // Set the camera position

    public GameObject wallPrefab;

    private List<(Vector3 position, Color color)> gizmoPoints = new List<(Vector3 position, Color color)>(); // Gizmo data

    private GameObject roomObject; // Room parent object

    private ErrorCalculator errorCalculator;

    private void Start()
    {
        // Create the empty room object
        roomObject = new GameObject("Room");
        roomObject.transform.position = Vector3.zero;
        roomObject.transform.rotation = Quaternion.identity;
        roomObject.transform.localScale = Vector3.one;

        if (roomCsvFile != null)
        {
            GenerateRoomFromCSV();
        }

        if (objectCsvFile != null)
        {
            ParseCSVAndPlaceObjects();
        }

        errorCalculator = gameObject.GetComponent<ErrorCalculator>();
        errorCalculator.enabled = true;
        errorCalculator.room = roomObject;
    }

    void GenerateRoomFromCSV()
    {
        string[] lines = roomCsvFile.text.Split('\n');
        if (lines.Length == 0) return;

        float minX = float.MaxValue, minY = float.MaxValue, minZ = float.MaxValue;
        float maxX = float.MinValue, maxY = float.MinValue, maxZ = float.MinValue;

        foreach (string line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            string[] values = line.Split(',');

            float x = float.Parse(values[1]);
            float y = float.Parse(values[2]);
            float z = float.Parse(values[3]);

            // Update min and max values
            minX = Mathf.Min(minX, x);
            minY = Mathf.Min(minY, y);
            minZ = Mathf.Min(minZ, z);

            maxX = Mathf.Max(maxX, x);
            maxY = Mathf.Max(maxY, y);
            maxZ = Mathf.Max(maxZ, z);
        }

        // Compute room dimensions
        float width = maxX - minX;
        float height = maxY - minY;
        float depth = maxZ - minZ;

        // Generate walls
        GenerateWall(new Vector3(width / 2, height/2, 0), new Vector3(width, height, 0.1f)); // Front wall
        GenerateWall(new Vector3(width / 2, height / 2, depth), new Vector3(width, height, 0.1f)); // Back wall
        GenerateWall(new Vector3(0, height / 2, depth / 2), new Vector3(0.1f, height, depth)); // Left wall
        GenerateWall(new Vector3(width, height / 2, depth / 2), new Vector3(0.1f, height, depth)); // Right wall
    }

    void GenerateWall(Vector3 position, Vector3 scale)
    {
        // Ensure wallPrefab is assigned in the Unity Inspector or instantiated elsewhere
        if (wallPrefab == null)
        {
            Debug.LogError("wallPrefab is not assigned. Please assign it in the Inspector.");
            return;
        }

        // Instantiate the wallPrefab at the specified position
        GameObject wall = Instantiate(wallPrefab, position, Quaternion.identity);

        // Set the scale of the wall
        wall.transform.localScale = scale;

        // Rename the wall object
        wall.name = "Wall";

        // Parent the wall to the room object
        wall.transform.SetParent(roomObject.transform);
    }


    void ParseCSVAndPlaceObjects()
    {
        string[] lines = objectCsvFile.text.Split('\n');
        foreach (string line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            string[] values = line.Split(',');

            int objectID = Mathf.RoundToInt(float.Parse(values[0]));

            Vector3 relativePosition = new Vector3(
                float.Parse(values[1]),
                float.Parse(values[2]),
                float.Parse(values[3])
            );
            Quaternion rotation = Quaternion.Euler(
                float.Parse(values[4]),
                float.Parse(values[5]),
                float.Parse(values[6])
            );

            Vector3 worldPosition = cameraPosition + relativePosition;
            
            List<Vector3> keypoints = new List<Vector3>();
            for (int i = 7; i < values.Length; i += 3)
            {
                if (i + 2 >= values.Length) break;

                Vector3 keypoint = new Vector3(
                    float.Parse(values[i]),
                    float.Parse(values[i + 1]),
                    float.Parse(values[i + 2])
                );
                keypoints.Add(cameraPosition + keypoint);
            }

            PlaceObject(objectID, worldPosition, rotation, keypoints);
        }
    }

    void PlaceObject(int objectID, Vector3 position, Quaternion rotation, List<Vector3> keypoints)
    {
        if (objectID >= 0 && objectID < objectPrefabs.Count)
        {
            GameObject prefab = objectPrefabs[objectID];
            if (prefab != null)
            {
                GameObject obj = Instantiate(prefab, position, rotation);

                // Parent the instantiated object to the room object
                obj.transform.SetParent(roomObject.transform);
            }
        }

        foreach (var keypoint in keypoints)
        {
            gizmoPoints.Add((keypoint, GetColorByID(objectID)));
        }
    }

    Color GetColorByID(int id)
    {
        return new Color(
            Mathf.Abs(Mathf.Sin(id * 0.5f)),
            Mathf.Abs(Mathf.Cos(id * 0.5f)),
            Mathf.Abs(Mathf.Sin(id * 0.3f))
        );
    }

    private void OnDrawGizmos()
    {
        if (gizmoPoints == null) return;

        foreach (var point in gizmoPoints)
        {
            Gizmos.color = point.color;
            Gizmos.DrawSphere(point.position, 0.1f);
        }
    }
}
