using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraIntrinsicParameterCalculator : MonoBehaviour
{
    void Start()
    {
        Camera cam = GetComponent<Camera>();

        // Get image dimensions
        float width = cam.pixelWidth;
        float height = cam.pixelHeight;

        // Calculate focal length based on field of view
        float fx = (width / 2.0f) / Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float fy = (height / 2.0f) / Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);

        // Principal point (usually the center of the image)
        float cx = width / 2.0f;
        float cy = height / 2.0f;

        // Construct the intrinsic matrix
        Matrix4x4 intrinsicMatrix = new Matrix4x4();
        intrinsicMatrix[0, 0] = fx;
        intrinsicMatrix[0, 1] = 0;
        intrinsicMatrix[0, 2] = cx;
        intrinsicMatrix[0, 3] = 0;

        intrinsicMatrix[1, 0] = 0;
        intrinsicMatrix[1, 1] = fy;
        intrinsicMatrix[1, 2] = cy;
        intrinsicMatrix[1, 3] = 0;

        intrinsicMatrix[2, 0] = 0;
        intrinsicMatrix[2, 1] = 0;
        intrinsicMatrix[2, 2] = 1;
        intrinsicMatrix[2, 3] = 0;

        intrinsicMatrix[3, 0] = 0;
        intrinsicMatrix[3, 1] = 0;
        intrinsicMatrix[3, 2] = 0;
        intrinsicMatrix[3, 3] = 1;

        Debug.Log("Intrinsic Matrix:\n" + intrinsicMatrix);
    }
}

