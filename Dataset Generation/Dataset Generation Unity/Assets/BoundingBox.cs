using UnityEngine;

public class BoundingBox : MonoBehaviour
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
        lineRenderer.loop = false; // We will connect manually without auto-looping
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
        // Get the overall bounds for this object and its children
        Bounds combinedBounds = CalculateCombinedBounds();

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

    // This function calculates the combined bounds of all renderers in this GameObject and its children
    private Bounds CalculateCombinedBounds()
    {
        Renderer[] renderers = GetComponentsInChildren<Renderer>();

        // If there are no renderers, return an empty bounds
        if (renderers.Length == 0)
        {
            return new Bounds(transform.position, Vector3.zero);
        }

        // Initialize the bounds to the first renderer's bounds
        Bounds combinedBounds = renderers[0].bounds;

        // Expand the bounds to include each renderer's bounds
        foreach (Renderer renderer in renderers)
        {
            combinedBounds.Encapsulate(renderer.bounds);
        }

        return combinedBounds;
    }

    // To show in the editor
    private void OnDrawGizmos()
    {
        Renderer[] renderers = GetComponentsInChildren<Renderer>();

        if (renderers.Length > 0)
        {
            Gizmos.color = boundingBoxColor;

            // Get the combined bounds for all renderers
            Bounds combinedBounds = CalculateCombinedBounds();

            // Draw the wireframe bounding box
            Gizmos.DrawWireCube(combinedBounds.center, combinedBounds.size);
        }
    }
}
