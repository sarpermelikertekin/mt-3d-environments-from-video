using UnityEngine;
using System.Collections.Generic;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class BoundingBoxWithoutRenderer : MonoBehaviour
{
    private LineRenderer lineRenderer;
    public Color boundingBoxColor = Color.green;
    public float lineWidth = 0.05f;

    // Dictionary to store the corners with labels
    private Dictionary<string, Vector3> cornersDict = new Dictionary<string, Vector3>();

    private void Start()
    {
        // Create a LineRenderer if it doesn't already exist
        lineRenderer = gameObject.GetComponent<LineRenderer>();
        if (lineRenderer == null)
        {
            lineRenderer = gameObject.AddComponent<LineRenderer>();
        }

        // Set the LineRenderer settings
        lineRenderer.useWorldSpace = true;
        lineRenderer.loop = false; // We will manually define the lines
        lineRenderer.startWidth = lineWidth;
        lineRenderer.endWidth = lineWidth;

        // Set glowing material
        Material glowMaterial = new Material(Shader.Find("Unlit/Color"));
        glowMaterial.color = boundingBoxColor;
        lineRenderer.material = glowMaterial;

        // Draw the bounding box and store corners
        DrawBoundingBox();
    }

    private void DrawBoundingBox()
    {
        // Calculate the bounding box from mesh vertices
        Bounds combinedBounds = CalculateMeshBounds();

        // Get the 8 corners of the bounding box and store them in a dictionary
        Vector3[] corners = new Vector3[8];
        corners[0] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);  // Top Front Right
        corners[1] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z); // Top Back Right
        corners[2] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z); // Top Back Left
        corners[3] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);  // Top Front Left
        corners[4] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);  // Bottom Front Right
        corners[5] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z); // Bottom Back Right
        corners[6] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z); // Bottom Back Left
        corners[7] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);  // Bottom Front Left

        // Store the corners in the dictionary with labels
        for (int i = 0; i < corners.Length; i++)
        {
            cornersDict["Corner" + i] = corners[i];
        }

        // Print the corner positions
        foreach (KeyValuePair<string, Vector3> corner in cornersDict)
        {
            Debug.Log(corner.Key + ": " + corner.Value);
        }

        // Set positions for LineRenderer to form the bounding box
        lineRenderer.positionCount = 16; // Only 12 edges of a cube, but we repeat to form a loop

        // Top square (connect corners 0, 1, 2, 3)
        lineRenderer.SetPosition(0, corners[0]);
        lineRenderer.SetPosition(1, corners[1]);
        lineRenderer.SetPosition(2, corners[2]);
        lineRenderer.SetPosition(3, corners[3]);
        lineRenderer.SetPosition(4, corners[0]);  // Close the top square loop

        // Bottom square (connect corners 4, 5, 6, 7)
        lineRenderer.SetPosition(5, corners[4]);
        lineRenderer.SetPosition(6, corners[5]);
        lineRenderer.SetPosition(7, corners[6]);
        lineRenderer.SetPosition(8, corners[7]);
        lineRenderer.SetPosition(9, corners[4]);  // Close the bottom square loop

        // Vertical edges (connect top and bottom squares)
        lineRenderer.SetPosition(10, corners[0]); // Top Front Right -> Bottom Front Right
        lineRenderer.SetPosition(11, corners[4]);

        lineRenderer.SetPosition(12, corners[1]); // Top Back Right -> Bottom Back Right
        lineRenderer.SetPosition(13, corners[5]);

        lineRenderer.SetPosition(14, corners[2]); // Top Back Left -> Bottom Back Left
        lineRenderer.SetPosition(15, corners[6]);

        lineRenderer.SetPosition(16, corners[3]); // Top Front Left -> Bottom Front Left
        lineRenderer.SetPosition(17, corners[7]);
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

    // To show in the editor
    private void OnDrawGizmos()
    {
        if (cornersDict.Count > 0)
        {
            Gizmos.color = boundingBoxColor;

            // Draw the bounding box corners as small spheres
            foreach (KeyValuePair<string, Vector3> corner in cornersDict)
            {
                Gizmos.DrawSphere(corner.Value, 0.05f);  // Draw a small sphere at each corner
            }

            // Draw the corner labels
#if UNITY_EDITOR
            foreach (KeyValuePair<string, Vector3> corner in cornersDict)
            {
                Handles.Label(corner.Value, corner.Key);  // Draw corner label
            }
#endif
        }
    }
}
