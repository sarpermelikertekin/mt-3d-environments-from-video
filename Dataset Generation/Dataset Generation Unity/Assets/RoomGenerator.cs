using UnityEngine;

public class RoomGenerator : MonoBehaviour
{
    // Room dimensions range (in units)
    public float minRoomWidth = 3f; // Minimum width of the room
    public float maxRoomWidth = 10f; // Maximum width of the room
    public float minRoomLength = 3f; // Minimum length of the room
    public float maxRoomLength = 10f; // Maximum length of the room
    public float wallThickness = 0.2f; // Thickness of the walls
    public float wallHeight = 3f; // Height of the walls
    public float objectBuffer = 1f; // Buffer to keep the object from spawning too close to walls

    // Prefabs for walls and objects
    public GameObject wallPrefab; // The wall prefab (cube-like object)
    public GameObject randomObjectPrefab; // The prefab for the object to place inside the room

    // Actual dimensions (randomized)
    private float roomWidth;
    private float roomLength;

    void Start()
    {
        // Randomize the room dimensions
        roomWidth = Random.Range(minRoomWidth, maxRoomWidth);
        roomLength = Random.Range(minRoomLength, maxRoomLength);

        GenerateRoom();
        SpawnRandomObject();
    }

    void GenerateRoom()
    {
        // Generate four walls using the prefab
        // Wall 1: Back wall (along Z-axis, width along X)
        CreateWall(new Vector3(roomWidth / 2, wallHeight / 2, 0), new Vector3(roomWidth, wallHeight, wallThickness));

        // Wall 2: Front wall (opposite to the back wall, along Z-axis)
        CreateWall(new Vector3(roomWidth / 2, wallHeight / 2, roomLength), new Vector3(roomWidth, wallHeight, wallThickness));

        // Wall 3: Left wall (along X-axis, length along Z)
        CreateWall(new Vector3(0, wallHeight / 2, roomLength / 2), new Vector3(wallThickness, wallHeight, roomLength));

        // Wall 4: Right wall (opposite to the left wall, along X-axis)
        CreateWall(new Vector3(roomWidth, wallHeight / 2, roomLength / 2), new Vector3(wallThickness, wallHeight, roomLength));

        // Generate floor
        CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength));
    }

    // Helper function to create a wall using a prefab
    void CreateWall(Vector3 position, Vector3 scale)
    {
        GameObject wall = Instantiate(wallPrefab); // Instantiate the wall prefab
        wall.transform.position = position; // Set position of the wall
        wall.transform.localScale = scale; // Set the scale (size) of the wall
        wall.transform.parent = this.transform; // Set the wall as a child of the RoomGenerator object
    }

    // Helper function to create a floor
    void CreateFloor(Vector3 position, Vector3 scale)
    {
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane); // Create a plane primitive for the floor
        floor.transform.position = position; // Set position of the floor
        floor.transform.localScale = new Vector3(scale.x / 10, 1, scale.z / 10); // Scale the plane (planes scale 10x smaller)
        floor.transform.parent = this.transform; // Set the floor as a child of the RoomGenerator object
    }

    // Function to spawn a random object inside the room
    void SpawnRandomObject()
    {
        // Calculate random position within the room but with a buffer from the walls
        float randomX = Random.Range(objectBuffer, roomWidth - objectBuffer);
        float randomZ = Random.Range(objectBuffer, roomLength - objectBuffer);

        // Instantiate the object at the random position
        Vector3 randomPosition = new Vector3(randomX, 0f, randomZ); // Assuming object height is small, position it slightly above the floor
        GameObject randomObject = Instantiate(randomObjectPrefab, randomPosition, Quaternion.identity);
        randomObject.transform.parent = this.transform; // Set the object as a child of the RoomGenerator object
    }
}
