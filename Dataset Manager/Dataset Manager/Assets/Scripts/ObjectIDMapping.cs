using System.Collections.Generic;

public static class ObjectNameToIDMapper
{
    // Static dictionary to store mappings from name to ID
    private static readonly Dictionary<string, int> NameToID = new Dictionary<string, int>
    {
        { "Chair", 0 },
        { "Desk", 1 },
        { "Laptop", 2 },
        { "Monitor", 3 },
        { "Window", 4 },
        { "Door", 5 },
        { "Sofa", 6 },
        { "Cabinet", 7 },
        { "Edge", 8 }
    };

    // Static dictionary to store mappings from ID to name
    private static readonly Dictionary<int, string> IDToName;

    // Static constructor to initialize the IDToName dictionary
    static ObjectNameToIDMapper()
    {
        IDToName = new Dictionary<int, string>();
        foreach (var kvp in NameToID)
        {
            IDToName[kvp.Value] = kvp.Key;
        }
    }

    // Retrieve ID from name
    public static int GetID(string name)
    {
        foreach (var mapping in NameToID)
        {
            if (name.Contains(mapping.Key))
            {
                return mapping.Value;
            }
        }

        return -1; // Default for unrecognized objects
    }

    // Retrieve name from ID
    public static string GetName(int id)
    {
        if (IDToName.TryGetValue(id, out string name))
        {
            return name;
        }

        return null; // Default for unrecognized IDs
    }
}
