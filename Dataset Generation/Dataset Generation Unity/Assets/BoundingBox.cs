using UnityEngine;
using System.Collections.Generic;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class BoundingBox : MonoBehaviour
{
    public Color boundingBoxColor = Color.green;
    public Vector3[] corners;

    private Dictionary<string, Vector3> cornersDict = new Dictionary<string, Vector3>();

    private void OnDrawGizmos()
    {
        // Calculate the bounding box from mesh vertices
        Bounds combinedBounds = CalculateMeshBounds();

        // Get the 8 corners of the bounding box
        corners = new Vector3[8];
        corners[0] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);  // Top Front Right
        corners[1] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z); // Top Back Right
        corners[2] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z); // Top Back Left
        corners[3] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);  // Top Front Left
        corners[4] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);  // Bottom Front Right
        corners[5] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z); // Bottom Back Right
        corners[6] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z); // Bottom Back Left
        corners[7] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);  // Bottom Front Left

        // Store corners in the dictionary with labels (optional)
        for (int i = 0; i < corners.Length; i++)
        {
            cornersDict["Corner" + i] = corners[i];
        }

        // Set the color for the bounding box
        Gizmos.color = boundingBoxColor;

        // Draw top square (connect corners 0, 1, 2, 3)
        Gizmos.DrawLine(corners[0], corners[1]);
        Gizmos.DrawLine(corners[1], corners[2]);
        Gizmos.DrawLine(corners[2], corners[3]);
        Gizmos.DrawLine(corners[3], corners[0]);

        // Draw bottom square (connect corners 4, 5, 6, 7)
        Gizmos.DrawLine(corners[4], corners[5]);
        Gizmos.DrawLine(corners[5], corners[6]);
        Gizmos.DrawLine(corners[6], corners[7]);
        Gizmos.DrawLine(corners[7], corners[4]);

        // Draw vertical edges (connect top and bottom squares)
        Gizmos.DrawLine(corners[0], corners[4]);  // Top Front Right -> Bottom Front Right
        Gizmos.DrawLine(corners[1], corners[5]);  // Top Back Right -> Bottom Back Right
        Gizmos.DrawLine(corners[2], corners[6]);  // Top Back Left -> Bottom Back Left
        Gizmos.DrawLine(corners[3], corners[7]);  // Top Front Left -> Bottom Front Left

#if UNITY_EDITOR
        // Create a GUIStyle to customize the label color
        GUIStyle labelStyle = new GUIStyle();
        labelStyle.normal.textColor = Color.black;
        labelStyle.fontStyle = FontStyle.Bold;

        // Get the screen position of the game object in the Scene view
        Vector3 labelPosition = transform.position;

        // Draw a green background rectangle behind the name label
        Handles.BeginGUI();
        {
            Vector3 screenPosition = HandleUtility.WorldToGUIPoint(labelPosition);
            Rect labelRect = new Rect(screenPosition.x - 50, screenPosition.y - 10, 100, 20); // Adjust the size and position of the rectangle

            // Draw the green background
            EditorGUI.DrawRect(labelRect, Color.green);

            // Display the name of the GameObject over the green background
            GUI.Label(labelRect, gameObject.name, labelStyle);
        }
        Handles.EndGUI();

        // Draw labels for each corner in the Scene view with green background
        foreach (KeyValuePair<string, Vector3> corner in cornersDict)
        {
            Handles.BeginGUI();
            {
                Vector3 cornerScreenPosition = HandleUtility.WorldToGUIPoint(corner.Value);
                Rect cornerLabelRect = new Rect(cornerScreenPosition.x - 40, cornerScreenPosition.y - 10, 80, 20); // Adjust size and position

                // Draw the green background for each corner label
                EditorGUI.DrawRect(cornerLabelRect, Color.green);

                // Display the corner label over the green background
                GUI.Label(cornerLabelRect, corner.Key, labelStyle);
            }
            Handles.EndGUI();
        }
#endif
    }

    // This function calculates the combined bounds of all MeshFilters in this GameObject and its children
    private Bounds CalculateMeshBounds()
    {
        MeshFilter[] meshFilters = GetComponentsInChildren<MeshFilter>();

        // If there are no mesh filters, return an empty bounds
        if (meshFilters.Length == 0)
        {
            return new Bounds(transform.position, Vector3.zero);
        }

        // Initialize the bounds to the first mesh's bounds
        Bounds combinedBounds = meshFilters[0].mesh.bounds;
        combinedBounds = TransformBounds(combinedBounds, meshFilters[0].transform);

        // Expand the bounds to include each mesh's bounds
        foreach (MeshFilter meshFilter in meshFilters)
        {
            Bounds meshBounds = TransformBounds(meshFilter.mesh.bounds, meshFilter.transform);
            combinedBounds.Encapsulate(meshBounds);
        }

        return combinedBounds;
    }

    // Transform local bounds to world space
    private Bounds TransformBounds(Bounds localBounds, Transform transform)
    {
        Vector3 worldCenter = transform.TransformPoint(localBounds.center);
        Vector3 worldExtents = transform.TransformVector(localBounds.extents);
        return new Bounds(worldCenter, worldExtents * 2);
    }
}
