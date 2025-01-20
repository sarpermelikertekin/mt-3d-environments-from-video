using UnityEngine;

public class MaterialHandler : MonoBehaviour
{
    // Public array to assign materials from in the Inspector
    public Material[] materials;

    // Automatically called when the script is initialized
    private void Start()
    {
        // Call the method to assign random materials to all children with MeshRenderer
        AssignRandomMaterialsToChildren();
    }

    // Function to assign random materials to all children (and deeper levels) with MeshRenderer
    private void AssignRandomMaterialsToChildren()
    {
        // Check if the materials array is not empty
        if (materials == null || materials.Length == 0)
        {
            Debug.LogWarning("No materials available in the materials array.");
            return;
        }

        // Get all children and deeper levels with MeshRenderer
        MeshRenderer[] meshRenderers = GetComponentsInChildren<MeshRenderer>();

        // Loop through each child with a MeshRenderer and assign a random material
        foreach (MeshRenderer renderer in meshRenderers)
        {
            // Randomly select a material from the array
            Material randomMaterial = materials[Random.Range(0, materials.Length)];

            // Assign the random material to the renderer
            renderer.material = randomMaterial;
        }
    }
}
