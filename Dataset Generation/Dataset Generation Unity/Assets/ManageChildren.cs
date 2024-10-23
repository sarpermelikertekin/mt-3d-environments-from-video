using UnityEngine;

public class DeactivateReactivateChildren : MonoBehaviour
{
    // Automatically called when the script is initialized
    private void Start()
    {
        // Call the method to deactivate all first-level children and randomly activate one
        DeactivateAndActivateRandomChild();
    }

    // Function to deactivate all first-level children and randomly activate one
    public void DeactivateAndActivateRandomChild()
    {
        // Get the number of first-level children
        int childCount = transform.childCount;

        // Ensure there is at least one child to activate
        if (childCount == 0)
        {
            Debug.LogWarning("No child objects available to activate.");
            return;
        }

        // Deactivate all first-level child objects
        for (int i = 0; i < childCount; i++)
        {
            transform.GetChild(i).gameObject.SetActive(false);
        }

        // Choose a random child to activate
        int randomIndex = Random.Range(0, childCount);
        transform.GetChild(randomIndex).gameObject.SetActive(true);
    }
}
