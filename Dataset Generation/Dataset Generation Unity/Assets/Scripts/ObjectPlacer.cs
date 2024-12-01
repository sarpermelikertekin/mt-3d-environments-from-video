using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class ObjectPlacer : MonoBehaviour
{
    [Header("CSV File")]
    public TextAsset csvFile;

    [Header("Prefabs")]
    public List<GameObject> objectPrefabs; // Assign prefabs for each ID in order

    [Header("Camera Settings")]
    public Vector3 cameraPosition; // Set the camera position

    private List<(Vector3 position, Color color)> gizmoPoints = new List<(Vector3 position, Color color)>(); // Gizmo data

    private void Start()
    {
        ParseCSVAndPlaceObjects();
    }

    void ParseCSVAndPlaceObjects()
    {
        if (csvFile == null)
        {
            Debug.LogError("CSV file not assigned.");
            return;
        }

        string[] lines = csvFile.text.Split('\n');
        foreach (string line in lines)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;

            string[] values = line.Split(',');

            // Parse object ID
            int objectID = Mathf.RoundToInt(float.Parse(values[0]));

            // Parse position and rotation
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

            // Transform to world position relative to the origin
            Vector3 worldPosition = cameraPosition + relativePosition;

            // Parse keypoints
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

            // Place object and visualize keypoints
            PlaceObject(objectID, worldPosition, rotation, keypoints);
        }
    }

    void PlaceObject(int objectID, Vector3 position, Quaternion rotation, List<Vector3> keypoints)
    {
        // Instantiate object if prefab exists for the given ID
        if (objectID >= 0 && objectID < objectPrefabs.Count)
        {
            GameObject prefab = objectPrefabs[objectID];
            if (prefab != null)
            {
                Instantiate(prefab, position, rotation);
            }
        }

        // Add keypoints to Gizmo drawing list
        foreach (var keypoint in keypoints)
        {
            gizmoPoints.Add((keypoint, GetColorByID(objectID)));
        }
    }

    Color GetColorByID(int id)
    {
        // Generate a consistent color for each ID
        return new Color(
            Mathf.Abs(Mathf.Sin(id * 0.5f)),
            Mathf.Abs(Mathf.Cos(id * 0.5f)),
            Mathf.Abs(Mathf.Sin(id * 0.3f))
        );
    }

    private void OnDrawGizmos()
    {
        // Draw keypoints with Gizmos
        if (gizmoPoints == null) return;

        foreach (var point in gizmoPoints)
        {
            Gizmos.color = point.color;
            Gizmos.DrawSphere(point.position, 0.1f); // Draw small spheres for keypoints
        }
    }
}
