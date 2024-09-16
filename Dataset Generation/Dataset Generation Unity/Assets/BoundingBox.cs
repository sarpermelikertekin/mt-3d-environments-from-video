using UnityEngine;

public class BoundingBoxWithoutRenderer : MonoBehaviour
{
    private LineRenderer lineRenderer;
    public Color boundingBoxColor = Color.green;
    public float lineWidth = 0.05f;

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

        DrawBoundingBox();
    }

    private void DrawBoundingBox()
    {
        // Calculate the bounding box from mesh vertices
        Bounds combinedBounds = CalculateMeshBounds();

        // Get the 8 corners of the bounding box
        Vector3[] corners = new Vector3[8];
        corners[0] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);
        corners[1] = combinedBounds.center + new Vector3(combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z);
        corners[2] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, -combinedBounds.extents.z);
        corners[3] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, combinedBounds.extents.y, combinedBounds.extents.z);
        corners[4] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);
        corners[5] = combinedBounds.center + new Vector3(combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z);
        corners[6] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, -combinedBounds.extents.z);
        corners[7] = combinedBounds.center + new Vector3(-combinedBounds.extents.x, -combinedBounds.extents.y, combinedBounds.extents.z);

        // Set positions for LineRenderer to form the bounding box
        lineRenderer.positionCount = 24; // We need 24 points to draw the full box correctly

        // Top square
        lineRenderer.SetPosition(0, corners[0]);
        lineRenderer.SetPosition(1, corners[1]);
        lineRenderer.SetPosition(2, corners[2]);
        lineRenderer.SetPosition(3, corners[3]);
        lineRenderer.SetPosition(4, corners[0]);  // Loop back to start of the top square

        // Bottom square
        lineRenderer.SetPosition(5, corners[4]);
        lineRenderer.SetPosition(6, corners[5]);
        lineRenderer.SetPosition(7, corners[6]);
        lineRenderer.SetPosition(8, corners[7]);
        lineRenderer.SetPosition(9, corners[4]);  // Loop back to start of the bottom square

        // Connect top and bottom squares
        lineRenderer.SetPosition(10, corners[0]);
        lineRenderer.SetPosition(11, corners[4]);

        lineRenderer.SetPosition(12, corners[1]);
        lineRenderer.SetPosition(13, corners[5]);

        lineRenderer.SetPosition(14, corners[2]);
        lineRenderer.SetPosition(15, corners[6]);

        lineRenderer.SetPosition(16, corners[3]);
        lineRenderer.SetPosition(17, corners[7]);

        // Additional connections to make it look proper (to fix diagonals)
        lineRenderer.SetPosition(18, corners[0]);  // Back to first point of top square to close the box
        lineRenderer.SetPosition(19, corners[3]);

        lineRenderer.SetPosition(20, corners[4]);  // Back to first point of bottom square
        lineRenderer.SetPosition(21, corners[7]);

        lineRenderer.SetPosition(22, corners[2]);  // Connect side diagonals if necessary (optional)
        lineRenderer.SetPosition(23, corners[6]);
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
        MeshFilter[] meshFilters = GetComponentsInChildren<MeshFilter>();

        if (meshFilters.Length > 0)
        {
            Gizmos.color = boundingBoxColor;

            // Get the combined bounds for all meshes
            Bounds combinedBounds = CalculateMeshBounds();

            // Draw the wireframe bounding box
            Gizmos.DrawWireCube(combinedBounds.center, combinedBounds.size);
        }
    }
}
