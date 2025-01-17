using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEngine;

public class ErrorCalculator : MonoBehaviour
{
    public GameObject groundTruth;
    public GameObject room;
    public string savePath = @"C:\Users\sakar\OneDrive\mt-datas\Pipeline"; // Path to save the report
    public string method = "";

    void Start()
    {
        // Automatically find and assign the groundTruth object if its name contains "Ground Truth"
        if (groundTruth == null)
        {
            GameObject[] allObjects = GameObject.FindObjectsOfType<GameObject>(); // Get all objects in the scene
            foreach (GameObject obj in allObjects)
            {
                if (obj.name.Contains("Ground Truth", System.StringComparison.OrdinalIgnoreCase))
                {
                    groundTruth = obj;
                    break;
                }
            }

            if (groundTruth == null)
            {
                Debug.LogError("Ground Truth object not found in the scene.");
                return;
            }
        }

        CompareObjects();
    }

    void CompareObjects()
    {
        if (groundTruth == null || room == null)
        {
            Debug.LogError("groundTruth or room object is not assigned.");
            return;
        }

        string report = "";

        // ---- Object Comparison ----

        // Generate normalized object counts for groundTruth and room
        Dictionary<int, int> groundTruthCounts = GetNormalizedObjectCounts(groundTruth);
        Dictionary<int, int> roomCounts = GetNormalizedObjectCounts(room);

        // Generate reports for both
        report += "Ground Truth Object Report:\n";
        foreach (var kvp in groundTruthCounts)
        {
            report += $"{GetCategoryName(kvp.Key)}: {kvp.Value}\n";
        }

        report += "\nRoom Object Report:\n";
        foreach (var kvp in roomCounts)
        {
            report += $"{GetCategoryName(kvp.Key)}: {kvp.Value}\n";
        }

        // Compare the counts
        report += "\nObject Comparison Report:\n";
        HashSet<int> allCategories = new HashSet<int>(groundTruthCounts.Keys.Union(roomCounts.Keys));
        foreach (int category in allCategories)
        {
            groundTruthCounts.TryGetValue(category, out int groundTruthCount);
            roomCounts.TryGetValue(category, out int roomCount);

            if (groundTruthCount != roomCount)
            {
                report += $"{GetCategoryName(category)}: GroundTruth has {groundTruthCount}, Room has {roomCount}\n";
            }
        }

        // ---- Room Size Comparison ----

        Vector3 groundTruthSize = MeasureRoomSize(groundTruth);
        Vector3 roomSize = MeasureRoomSize(room);

        report += $"\nGround Truth Room Size: X={groundTruthSize.x}, Y={groundTruthSize.y}, Z={groundTruthSize.z}\n";
        report += $"Generated Room Size: X={roomSize.x}, Y={roomSize.y}, Z={roomSize.z}\n";

        // Compare room sizes
        report += "\nRoom Size Comparison Report:\n";
        report += $"X Difference: {Mathf.Abs(groundTruthSize.x - roomSize.x)}\n";
        report += $"Y Difference: {Mathf.Abs(groundTruthSize.y - roomSize.y)}\n";
        report += $"Z Difference: {Mathf.Abs(groundTruthSize.z - roomSize.z)}\n";

        // ---- Nearest Object Distance Calculation ----

        report += CalculateNearestObjectDistances();

        // Save the report
        SaveReport(report);
    }

    string CalculateNearestObjectDistances()
    {
        float totalDistance = 0f;
        int matchedObjects = 0;
        string distanceReport = "\nNearest Object Distance Report:\n";

        foreach (Transform groundTruthChild in groundTruth.transform)
        {
            if (ShouldIgnoreObject(groundTruthChild.name)) continue;

            string groundTruthName = NormalizeName(groundTruthChild.name);
            Transform nearestObject = null;
            float nearestDistance = float.MaxValue;

            foreach (Transform roomChild in room.transform)
            {
                if (ShouldIgnoreObject(roomChild.name)) continue;

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
                float rotationDifference = Quaternion.Angle(groundTruthChild.rotation, nearestObject.rotation);
                distanceReport += $"Nearest object to {groundTruthChild.name} is {nearestObject.name} with distance {nearestDistance:F2} and rotation difference {rotationDifference:F2} degrees\n";
                totalDistance += nearestDistance;
                matchedObjects++;
            }
            else
            {
                distanceReport += $"No matching object found for {groundTruthChild.name} in the room.\n";
            }
        }

        if (matchedObjects > 0)
        {
            float averageDistance = totalDistance / matchedObjects;
            distanceReport += $"Average distance between matched objects: {averageDistance:F2}\n";
        }
        else
        {
            distanceReport += "No matched objects to calculate average distance.\n";
        }

        Debug.Log(distanceReport);
        return distanceReport;
    }

    void SaveReport(string report)
    {
        string snakeCaseName = ConvertToSnakeCase(groundTruth.name);
        string fileName = $"{snakeCaseName}_{method}_report.txt";
        string filePath = Path.Combine(savePath, fileName);

        try
        {
            File.WriteAllText(filePath, report);
            Debug.Log($"Report saved successfully at: {filePath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to save report: {ex.Message}");
        }
    }

    string ConvertToSnakeCase(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;

        string snakeCase = Regex.Replace(input, @"([a-z])([A-Z])", "$1_$2").ToLower();
        snakeCase = Regex.Replace(snakeCase, @"\s+", "_"); // Replace spaces with underscores
        snakeCase = Regex.Replace(snakeCase, @"[^a-z0-9_]", ""); // Remove invalid characters
        return snakeCase;
    }

    string NormalizeName(string name)
    {
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
            if (ShouldIgnoreObject(child.name)) continue;

            int category = CategorizeObject(child.name);

            if (category >= 0)
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
        if (name.Contains("Vertex")) return 0;
        else if (name.Contains("Cabinet")) return 1;
        else if (name.Contains("Common Chair")) return 2;
        else if (name.Contains("Desk")) return 3;
        else if (name.Contains("Door")) return 4;
        else if (name.Contains("Laptop")) return 5;
        else if (name.Contains("Monitor")) return 6;
        else if (name.Contains("Office Chair")) return 7;
        else if (name.Contains("Pendant")) return 8;
        else if (name.Contains("Robotic Arm")) return 9;
        else if (name.Contains("Sofa")) return 10;
        else if (name.Contains("Window")) return 11;
        else return -1;  // Default for unrecognized objects
    }


    string GetCategoryName(int category)
    {
        switch (category)
        {
            case 0: return "Vertex";
            case 1: return "Cabinet";
            case 2: return "Common Chair";
            case 3: return "Desk";
            case 4: return "Door";
            case 5: return "Laptop";
            case 6: return "Monitor";
            case 7: return "Office Chair";
            case 8: return "Pendant";
            case 9: return "Robotic Arm";
            case 10: return "Sofa";
            case 11: return "Window";
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
            Vector3 position = child.position;

            minX = Mathf.Min(minX, position.x);
            minZ = Mathf.Min(minZ, position.z);
            maxX = Mathf.Max(maxX, position.x);
            maxZ = Mathf.Max(maxZ, position.z);

            sizeY = Mathf.Max(sizeY, child.localScale.y);
        }

        float sizeX = maxX - minX;
        float sizeZ = maxZ - minZ;

        return new Vector3(sizeX, sizeY, sizeZ);
    }

    bool ShouldIgnoreObject(string name)
    {
        return name.Contains("Wall") || name.Contains("Vertex") || name.Contains("Point Light") || name.Contains("Plane");
    }
}
