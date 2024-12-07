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

        // ---- Object Comparison ----

        // Generate normalized object counts for groundTruth and room
        Dictionary<int, int> groundTruthCounts = GetNormalizedObjectCounts(groundTruth);
        Dictionary<int, int> roomCounts = GetNormalizedObjectCounts(room);

        // Generate reports for both
        Debug.Log("Ground Truth Object Report:");
        foreach (var kvp in groundTruthCounts)
        {
            Debug.Log($"{GetCategoryName(kvp.Key)}: {kvp.Value}");
        }

        Debug.Log("Room Object Report:");
        foreach (var kvp in roomCounts)
        {
            Debug.Log($"{GetCategoryName(kvp.Key)}: {kvp.Value}");
        }

        // Compare the counts
        Debug.Log("Object Comparison Report:");
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

        // ---- Room Size Comparison ----

        Vector3 groundTruthSize = MeasureRoomSize(groundTruth);
        Vector3 roomSize = MeasureRoomSize(room);

        // Report room sizes
        Debug.Log($"Ground Truth Room Size: X={groundTruthSize.x}, Y={groundTruthSize.y}, Z={groundTruthSize.z}");
        Debug.Log($"Generated Room Size: X={roomSize.x}, Y={roomSize.y}, Z={roomSize.z}");

        // Compare room sizes
        Debug.Log("Room Size Comparison Report:");
        Debug.Log($"X Difference: {Mathf.Abs(groundTruthSize.x - roomSize.x)}");
        Debug.Log($"Y Difference: {Mathf.Abs(groundTruthSize.y - roomSize.y)}");
        Debug.Log($"Z Difference: {Mathf.Abs(groundTruthSize.z - roomSize.z)}");

        // ---- Nearest Object Distance Calculation ----

        CalculateNearestObjectDistances();
    }

    void CalculateNearestObjectDistances()
    {
        float totalDistance = 0f;
        int matchedObjects = 0;

        foreach (Transform groundTruthChild in groundTruth.transform)
        {
            string groundTruthName = NormalizeName(groundTruthChild.name);
            Transform nearestObject = null;
            float nearestDistance = float.MaxValue;

            foreach (Transform roomChild in room.transform)
            {
                string roomName = NormalizeName(roomChild.name);

                if (groundTruthName == roomName)
                {
                    float distance = Vector3.Distance(groundTruthChild.position, roomChild.position);
                    if (distance < nearestDistance)
                    {
                        nearestDistance = distance;
                        nearestObject = roomChild;
                    }
                }
            }

            if (nearestObject != null)
            {
                Debug.Log($"Nearest object to {groundTruthChild.name} is {nearestObject.name} with distance {nearestDistance:F2}");
                totalDistance += nearestDistance;
                matchedObjects++;
            }
            else
            {
                Debug.Log($"No matching object found for {groundTruthChild.name} in the room.");
            }
        }

        // Calculate and report the average distance
        if (matchedObjects > 0)
        {
            float averageDistance = totalDistance / matchedObjects;
            Debug.Log($"Average distance between matched objects: {averageDistance:F2}");
        }
        else
        {
            Debug.Log("No matched objects to calculate average distance.");
        }
    }

    string NormalizeName(string name)
    {
        // Normalizes names by removing variations like " (Clone)" or numbering
        int index = name.IndexOf(' ');
        if (index > 0) name = name.Substring(0, index);

        index = name.IndexOf('(');
        if (index > 0) name = name.Substring(0, index);

        return name.Trim();
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

    Vector3 MeasureRoomSize(GameObject parent)
    {
        float minX = float.MaxValue, minZ = float.MaxValue;
        float maxX = float.MinValue, maxZ = float.MinValue;
        float sizeY = 0;

        foreach (Transform child in parent.transform)
        {
            if (child.name.Contains("Wall")) // Check if the object is a wall
            {
                Vector3 position = child.position;

                // Update min and max values for X and Z
                minX = Mathf.Min(minX, position.x);
                minZ = Mathf.Min(minZ, position.z);
                maxX = Mathf.Max(maxX, position.x);
                maxZ = Mathf.Max(maxZ, position.z);

                // Update the Y dimension based on wall height
                sizeY = Mathf.Max(sizeY, child.localScale.y);
            }
        }

        // Calculate room size (dimensions)
        float sizeX = maxX - minX;
        float sizeZ = maxZ - minZ;

        return new Vector3(sizeX, sizeY, sizeZ);
    }

    void Start()
    {
        CompareObjects(); // Perform the comparison at the start
    }
}
