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

    // Camera control variables
    public Camera mainCamera; // Reference to the main camera
    public GameObject wallPrefab;
    public GameObject randomObjectPrefab;
    private Vector3[] cameraPositions; // Store 4 possible camera positions
    private int currentCameraIndex = 0; // Index to keep track of the current camera position
    public float cameraBuffer = 0.5f; // Buffer for camera positioning

    // Actual dimensions (randomized)
    private float roomWidth;
    private float roomLength;

    // To store the generated room elements
    private GameObject roomParent;

    void Start()
    {
        // Initial room generation
        //GenerateRoom();
        //SetupCameraPositions();
    }

    void Update()
    {
        // Check for key presses to generate/delete room or change camera position
        if (Input.GetKeyDown(KeyCode.P))
        {
            GenerateRoom();
            SetupCameraPositions(); // Reset camera positions after a new room is generated
        }

        if (Input.GetKeyDown(KeyCode.O))
        {
            DeleteRoom();
        }

        if (Input.GetKeyDown(KeyCode.I))
        {
            MoveToNextCameraPosition(); // Change the camera's position
        }
    }

    public void GenerateRoom()
    {
        // If a room already exists, delete it before creating a new one
        if (roomParent != null)
        {
            DeleteRoom();
        }

        // Create a new empty GameObject to hold the room elements
        roomParent = new GameObject("GeneratedRoom");

        // Randomize the room dimensions
        roomWidth = Random.Range(minRoomWidth, maxRoomWidth);
        roomLength = Random.Range(minRoomLength, maxRoomLength);

        // Generate the walls and floor
        // Wall 1: Back wall (along Z-axis, width along X)
        CreateWall(new Vector3(roomWidth / 2, wallHeight / 2, 0), new Vector3(roomWidth, wallHeight, wallThickness));

        // Wall 2: Front wall (opposite to the back wall, along Z-axis)
        CreateWall(new Vector3(roomWidth / 2, wallHeight / 2, roomLength), new Vector3(roomWidth, wallHeight, wallThickness));

        // Wall 3: Left wall (along X-axis, length along Z)
        CreateWall(new Vector3(0, wallHeight / 2, roomLength / 2), new Vector3(wallThickness, wallHeight, roomLength));

        // Wall 4: Right wall (opposite to the left wall, along X-axis)
        CreateWall(new Vector3(roomWidth, wallHeight / 2, roomLength / 2), new Vector3(wallThickness, wallHeight, roomLength));

        // Generate the floor
        CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength));

        // Generate the ceiling at the height of the wall
        CreateCeiling(new Vector3(roomWidth / 2, wallHeight, roomLength / 2), new Vector3(roomWidth, 1, roomLength));

        // Spawn a random object inside the room
        SpawnRandomObject();

        // Add a point light in the middle of the room at height 2.5
        CreatePointLight();
    }

    // Helper function to create a wall using the wall prefab
    void CreateWall(Vector3 position, Vector3 scale)
    {
        GameObject wall = Instantiate(wallPrefab); // Instantiate the wall prefab
        wall.transform.position = position; // Set position of the wall
        wall.transform.localScale = scale; // Set the scale (size) of the wall
        wall.transform.parent = roomParent.transform; // Parent the wall to roomParent
    }

    // Helper function to create the floor
    void CreateFloor(Vector3 position, Vector3 scale)
    {
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane); // Create a plane primitive for the floor
        floor.transform.position = position; // Set position of the floor
        floor.transform.localScale = new Vector3(scale.x / 10, 1, scale.z / 10); // Scale the plane (planes scale 10x smaller)
        floor.transform.parent = roomParent.transform; // Parent the floor to roomParent
    }

    // Helper function to create the ceiling
    void CreateCeiling(Vector3 position, Vector3 scale)
    {
        GameObject ceiling = GameObject.CreatePrimitive(PrimitiveType.Plane); // Create a plane primitive for the ceiling
        ceiling.transform.position = position; // Set position of the ceiling
        ceiling.transform.localScale = new Vector3(scale.x / 10, 1, scale.z / 10); // Scale the plane (planes scale 10x smaller)
        ceiling.transform.Rotate(180, 0, 0); // Rotate the ceiling to face downward
        ceiling.transform.parent = roomParent.transform; // Parent the ceiling to roomParent
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
        randomObject.transform.parent = roomParent.transform; // Parent the object to roomParent
    }

    // Function to create a point light at the center of the room
    void CreatePointLight()
    {
        // Create a new GameObject for the light
        GameObject lightGameObject = new GameObject("Point Light");
        Light pointLight = lightGameObject.AddComponent<Light>(); // Add a Light component

        // Set the light type to Point
        pointLight.type = LightType.Point;

        // Set the color to a "whiteish yellow" for room lighting
        pointLight.color = new Color(1.0f, 0.9f, 0.7f); // Light yellow color

        // Set the position of the point light to the center of the room at a height of 2.5f
        lightGameObject.transform.position = new Vector3(roomWidth / 2, 2.5f, roomLength / 2);

        // Set intensity and range (customize as needed)
        pointLight.intensity = 1.5f; // Set the brightness of the light
        pointLight.range = 10f; // Set the range of the light

        // Parent the light to the room parent object
        lightGameObject.transform.parent = roomParent.transform;
    }

    // Function to delete the generated room
    public void DeleteRoom()
    {
        if (roomParent != null)
        {
            Destroy(roomParent); // Destroys all children of roomParent (walls, floor, objects)
        }
    }

    // Setup camera positions in the 4 corners of the room, with a buffer
    public void SetupCameraPositions()
    {
        // Define the 4 corners of the room with a buffer of 0.5 units
        cameraPositions = new Vector3[4];
        cameraPositions[0] = new Vector3(cameraBuffer, 1.4f, cameraBuffer);  // Bottom-left corner with buffer
        cameraPositions[1] = new Vector3(roomWidth - cameraBuffer, 1.4f, cameraBuffer);  // Bottom-right corner with buffer
        cameraPositions[2] = new Vector3(cameraBuffer, 1.4f, roomLength - cameraBuffer);  // Top-left corner with buffer
        cameraPositions[3] = new Vector3(roomWidth - cameraBuffer, 1.4f, roomLength - cameraBuffer);  // Top-right corner with buffer

        // Reset camera index
        currentCameraIndex = 0;

        // Move camera to the first position
        MoveToCameraPosition(0);
    }

    // Function to move camera to the next position in the array
    public void MoveToNextCameraPosition()
    {
        currentCameraIndex = (currentCameraIndex + 1) % cameraPositions.Length;
        MoveToCameraPosition(currentCameraIndex);
    }

    // Function to move the camera to a specific position and apply rotation
    void MoveToCameraPosition(int index)
    {
        Vector3 cameraPosition = cameraPositions[index];

        // Ensure the camera's height is always 1.4f
        cameraPosition.y = 1.4f;

        // Look at the center of the room at the same height as the camera
        Vector3 lookAtTarget = new Vector3(roomWidth / 2, 1.4f, roomLength / 2);

        // Apply random rotation between -45 and 45 degrees
        Quaternion rotation = Quaternion.LookRotation(lookAtTarget - cameraPosition);
        rotation = Quaternion.Euler(rotation.eulerAngles.x, rotation.eulerAngles.y + Random.Range(-45f, 45f), rotation.eulerAngles.z);

        // Move the camera and apply rotation
        mainCamera.transform.position = cameraPosition;
        mainCamera.transform.rotation = rotation;
    }
}
