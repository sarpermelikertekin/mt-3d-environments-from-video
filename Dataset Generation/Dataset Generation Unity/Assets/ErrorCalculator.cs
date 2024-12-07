using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class ErrorCalculator : MonoBehaviour
{
    public GameObject groundTruth;
    public GameObject room;

    void CompareObjects()
    {
        if (groundTruth == null || room == null)
        {
            Debug.LogError("groundTruth or room object is not assigned.");
            return;
        }

        // Generate normalized object counts for groundTruth and room
        Dictionary<int, int> groundTruthCounts = GetNormalizedObjectCounts(groundTruth);
        Dictionary<int, int> roomCounts = GetNormalizedObjectCounts(room);

        // Generate reports for both
        Debug.Log("Ground Truth Report:");
        foreach (var kvp in groundTruthCounts)
        {
            Debug.Log($"{GetCategoryName(kvp.Key)}: {kvp.Value}");
        }

        Debug.Log("Room Report:");
        foreach (var kvp in roomCounts)
        {
            Debug.Log($"{GetCategoryName(kvp.Key)}: {kvp.Value}");
        }

        // Compare the counts
        Debug.Log("Comparison Report:");
        HashSet<int> allCategories = new HashSet<int>(groundTruthCounts.Keys.Union(roomCounts.Keys));
        foreach (int category in allCategories)
        {
            groundTruthCounts.TryGetValue(category, out int groundTruthCount);
            roomCounts.TryGetValue(category, out int roomCount);

            if (groundTruthCount != roomCount)
            {
                Debug.Log($"{GetCategoryName(category)}: GroundTruth has {groundTruthCount}, Room has {roomCount}");
            }
        }
    }

    Dictionary<int, int> GetNormalizedObjectCounts(GameObject parent)
    {
        Dictionary<int, int> objectCounts = new Dictionary<int, int>();

        foreach (Transform child in parent.transform)
        {
            int category = CategorizeObject(child.name);

            if (category >= 0) // Ignore unrecognized objects
            {
                if (!objectCounts.ContainsKey(category))
                {
                    objectCounts[category] = 0;
                }

                objectCounts[category]++;
            }
        }

        return objectCounts;
    }

    int CategorizeObject(string name)
    {
        // Normalized categories based on the object's name
        if (name.Contains("Chair")) return 0;
        else if (name.Contains("Desk")) return 1;
        else if (name.Contains("Laptop")) return 2;
        else if (name.Contains("Monitor")) return 3;
        else if (name.Contains("Window")) return 4;
        else if (name.Contains("Door")) return 5;
        else if (name.Contains("Sofa")) return 6;
        else if (name.Contains("Cabinet")) return 7;
        else return -1; // Unrecognized object
    }

    string GetCategoryName(int category)
    {
        // Human-readable names for categories
        switch (category)
        {
            case 0: return "Chair";
            case 1: return "Desk";
            case 2: return "Laptop";
            case 3: return "Monitor";
            case 4: return "Window";
            case 5: return "Door";
            case 6: return "Sofa";
            case 7: return "Cabinet";
            default: return "Unknown";
        }
    }

    void Start()
    {
        CompareObjects(); // Perform the comparison at the start
    }
}
