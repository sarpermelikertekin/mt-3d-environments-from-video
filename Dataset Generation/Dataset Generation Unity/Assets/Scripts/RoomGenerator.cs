using UnityEngine;
using System.Collections.Generic; // For using lists

public class RoomGenerator : MonoBehaviour
{
    public Material[] materialArray; // Array of possible materials for walls, floor, and ceiling
    public enum MaterialMode { AllSame, FloorDifferent, AllDifferent, EverySurfaceRandom }
    public MaterialMode materialMode = MaterialMode.AllSame; // Default mode

    // Prefabs for doors and windows
    public GameObject doorPrefab;
    public GameObject windowPrefab;
    public GameObject edgePrefab;

    // Room dimensions range (in units)
    public float minRoomWidth = 3f; // Minimum width of the room
    public float maxRoomWidth = 10f; // Maximum width of the room
    public float minRoomLength = 3f; // Minimum length of the room
    public float maxRoomLength = 10f; // Maximum length of the room
    public float minRoomHeight = 2f; // Minimum height of the walls
    public float maxRoomHeight = 4f; // Maximum height of the walls
    public float minCameraHeight = 1.2f; // Minimum height of the walls
    public float maxCameraHeight = 1.8f; // Maximum height of the walls
    public float wallThickness = 0.2f; // Thickness of the walls
    public float objectBuffer = 1f; // Buffer to keep the object from spawning too close to walls
    public float minObjectDistance = 2f; // Minimum distance between objects to prevent overlap

    // Camera control variables
    public Camera mainCamera; // Reference to the main camera
    public GameObject wallPrefab;
    public GameObject[] randomObjectPrefabs; // Array of object prefabs to randomly choose from
    public int maxObjectsToSpawn = 5; // Maximum number of objects to spawn randomly
    private Vector3[] cameraPositions; // Store 4 possible camera positions
    public int currentCameraIndex = 0; // Index to keep track of the current camera position
    public float cameraBuffer = 0.5f; // Buffer for camera positioning

    // Actual dimensions (randomized)
    private float roomWidth;
    private float roomLength;
    private float roomHeight;
    private float cameraHeight;


    // To store the generated room elements
    private GameObject roomParent;

    // List to store the positions of spawned objects
    private List<Vector3> spawnedObjectPositions = new List<Vector3>();

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
        roomParent = new GameObject("GeneratedRoom");

        roomWidth = Random.Range(minRoomWidth, maxRoomWidth);
        roomLength = Random.Range(minRoomLength, maxRoomLength);
        roomHeight = Random.Range(minRoomHeight, maxRoomHeight);

        materialMode = (MaterialMode)System.Enum.GetValues(typeof(MaterialMode))
            .GetValue(Random.Range(0, System.Enum.GetValues(typeof(MaterialMode)).Length));

        Material wallMaterial, floorMaterial, ceilingMaterial;
        Material wall1Material, wall2Material, wall3Material, wall4Material;

        switch (materialMode)
        {
            case MaterialMode.AllSame:
                wallMaterial = floorMaterial = ceilingMaterial = materialArray[Random.Range(0, materialArray.Length)];
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, 0), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.forward);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, roomLength), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.back);
                CreateWallWithDoorOrWindow(new Vector3(0, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.right);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.left);
                CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength), floorMaterial);
                CreateCeiling(new Vector3(roomWidth / 2, roomHeight, roomLength / 2), new Vector3(roomWidth, 1, roomLength), ceilingMaterial);
                break;

            case MaterialMode.FloorDifferent:
                wallMaterial = ceilingMaterial = materialArray[Random.Range(0, materialArray.Length)];
                floorMaterial = materialArray[Random.Range(0, materialArray.Length)];
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, 0), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.forward);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, roomLength), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.back);
                CreateWallWithDoorOrWindow(new Vector3(0, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.right);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.left);
                CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength), floorMaterial);
                CreateCeiling(new Vector3(roomWidth / 2, roomHeight, roomLength / 2), new Vector3(roomWidth, 1, roomLength), ceilingMaterial);
                break;

            case MaterialMode.AllDifferent:
                wallMaterial = materialArray[Random.Range(0, materialArray.Length)];
                floorMaterial = materialArray[Random.Range(0, materialArray.Length)];
                ceilingMaterial = materialArray[Random.Range(0, materialArray.Length)];
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, 0), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.forward);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, roomLength), new Vector3(roomWidth, roomHeight, wallThickness), wallMaterial, Vector3.back);
                CreateWallWithDoorOrWindow(new Vector3(0, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.right);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wallMaterial, Vector3.left);
                CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength), floorMaterial);
                CreateCeiling(new Vector3(roomWidth / 2, roomHeight, roomLength / 2), new Vector3(roomWidth, 1, roomLength), ceilingMaterial);
                break;

            case MaterialMode.EverySurfaceRandom:
                wall1Material = materialArray[Random.Range(0, materialArray.Length)];
                wall2Material = materialArray[Random.Range(0, materialArray.Length)];
                wall3Material = materialArray[Random.Range(0, materialArray.Length)];
                wall4Material = materialArray[Random.Range(0, materialArray.Length)];
                floorMaterial = materialArray[Random.Range(0, materialArray.Length)];
                ceilingMaterial = materialArray[Random.Range(0, materialArray.Length)];

                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, 0), new Vector3(roomWidth, roomHeight, wallThickness), wall1Material, Vector3.forward);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth / 2, roomHeight / 2, roomLength), new Vector3(roomWidth, roomHeight, wallThickness), wall2Material, Vector3.back);
                CreateWallWithDoorOrWindow(new Vector3(0, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wall3Material, Vector3.right);
                CreateWallWithDoorOrWindow(new Vector3(roomWidth, roomHeight / 2, roomLength / 2), new Vector3(wallThickness, roomHeight, roomLength), wall4Material, Vector3.left);
                CreateFloor(new Vector3(roomWidth / 2, 0, roomLength / 2), new Vector3(roomWidth, 1, roomLength), floorMaterial);
                CreateCeiling(new Vector3(roomWidth / 2, roomHeight, roomLength / 2), new Vector3(roomWidth, 1, roomLength), ceilingMaterial);
                break;
        }

        spawnedObjectPositions.Clear();
        int randomNumberOfObjects = Random.Range(1, maxObjectsToSpawn + 1);

        for (int i = 0; i < randomNumberOfObjects; i++)
        {
            SpawnRandomObject();
        }

        CreatePointLight();

        PlaceEdgePrefabs();
    }

    void PlaceEdgePrefabs()
    {
        if (edgePrefab == null)
        {
            Debug.LogWarning("Edge prefab is not assigned.");
            return;
        }

        // Define the four corner positions of the room
        Vector3[] cornerPositions = new Vector3[8];
        cornerPositions[0] = new Vector3(0, 0, 0); // Bottom-left corner on floor
        cornerPositions[1] = new Vector3(roomWidth, 0, 0); // Bottom-right corner on floor
        cornerPositions[2] = new Vector3(0, 0, roomLength); // Top-left corner on floor
        cornerPositions[3] = new Vector3(roomWidth, 0, roomLength); // Top-right corner on floor
        cornerPositions[4] = new Vector3(0, roomHeight, 0); // Top-left corner on ceiling
        cornerPositions[5] = new Vector3(roomWidth, roomHeight, 0); // Top-right corner on ceiling
        cornerPositions[6] = new Vector3(0, roomHeight, roomLength); // Bottom-left corner on ceiling
        cornerPositions[7] = new Vector3(roomWidth, roomHeight, roomLength); // Bottom-right corner on ceiling

        // Instantiate an edge prefab at each corner position
        foreach (Vector3 corner in cornerPositions)
        {
            GameObject edge = Instantiate(edgePrefab, corner, Quaternion.identity, roomParent.transform);
            edge.transform.position += new Vector3(wallThickness / 2, 0, wallThickness / 2); // Adjust for wall thickness
        }
    }

    void CreateWallWithDoorOrWindow(Vector3 position, Vector3 scale, Material material, Vector3 direction)
    {
        GameObject wall = Instantiate(wallPrefab, position, Quaternion.identity, roomParent.transform);
        wall.transform.localScale = scale;
        wall.GetComponent<Renderer>().material = material;

        // Decide randomly whether to place a door or window
        if (Random.value < 0.5f) return; // 50% chance to skip adding a door or window

        GameObject prefab = (Random.value < 0.5f) ? doorPrefab : windowPrefab;
        float yOffset = prefab == doorPrefab ? 0 : Random.Range(0.45f, 0.7f); // Door at y=0, window between 0.45 and 0.7
        float distanceFromWall = prefab == doorPrefab ? 0.2f : 0.1f;

        // Position and rotation based on wall direction
        Vector3 spawnPosition = position + direction * distanceFromWall;
        spawnPosition.y = yOffset;

        Quaternion rotation = Quaternion.identity;
        if (direction == Vector3.right) rotation = Quaternion.Euler(0, -90, 0);
        else if (direction == Vector3.left) rotation = Quaternion.Euler(0, 90, 0);
        else if (direction == Vector3.back) rotation = Quaternion.Euler(0, 180, 0);

        GameObject obj = Instantiate(prefab, spawnPosition, rotation, roomParent.transform);
    }

    void CreateFloor(Vector3 position, Vector3 scale, Material material)
    {
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.transform.position = position;
        floor.transform.localScale = new Vector3(scale.x / 10, 1, scale.z / 10);
        floor.transform.parent = roomParent.transform;
        floor.GetComponent<Renderer>().material = material;
    }

    void CreateCeiling(Vector3 position, Vector3 scale, Material material)
    {
        GameObject ceiling = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ceiling.transform.position = position;
        ceiling.transform.localScale = new Vector3(scale.x / 10, 1, scale.z / 10);
        ceiling.transform.Rotate(180, 0, 0);
        ceiling.transform.parent = roomParent.transform;
        ceiling.GetComponent<Renderer>().material = material;
    }


    // Function to spawn a random object inside the room with distance validation
    void SpawnRandomObject()
    {
        // Choose a random object prefab from the array
        GameObject randomObjectPrefab = randomObjectPrefabs[Random.Range(0, randomObjectPrefabs.Length)];

        // Initialize the random position with a default value (e.g., Vector3.zero)
        Vector3 randomPosition = Vector3.zero;

        // Try to find a position that's far enough from other objects
        int maxAttempts = 100; // Limit the number of attempts to avoid infinite loops
        bool positionIsValid = false;

        for (int attempts = 0; attempts < maxAttempts; attempts++)
        {
            // Calculate random position within the room but with a buffer from the walls
            float randomX = Random.Range(objectBuffer, roomWidth - objectBuffer);
            float randomZ = Random.Range(objectBuffer, roomLength - objectBuffer);
            randomPosition = new Vector3(randomX, 0f, randomZ);

            // Check if the position is valid (far enough from other objects)
            positionIsValid = true; // Assume the position is valid initially
            foreach (Vector3 otherPosition in spawnedObjectPositions)
            {
                if (Vector3.Distance(randomPosition, otherPosition) < minObjectDistance)
                {
                    positionIsValid = false; // If too close to another object, position is not valid
                    break;
                }
            }

            // If a valid position is found, break out of the loop
            if (positionIsValid)
            {
                break;
            }
        }

        // If a valid position is found, spawn the object
        if (positionIsValid)
        {
            // Generate a random Y rotation (0 to 360 degrees)
            //float randomYRotation = Random.Range(0f, 360f);
            //Quaternion randomRotation = Quaternion.Euler(0f, randomYRotation, 0f);

            // Instantiate the object with the random position and random Y-axis rotation
            GameObject randomObject = Instantiate(randomObjectPrefab, randomPosition, Quaternion.identity);
            randomObject.transform.parent = roomParent.transform; // Parent the object to roomParent
            spawnedObjectPositions.Add(randomPosition); // Store the position of the spawned object
        }
        else
        {
            Debug.LogWarning("Failed to find a valid position for the object after multiple attempts.");
        }
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
        cameraHeight = Random.Range(minCameraHeight, maxCameraHeight);

        // Define the 4 corners of the room with a buffer of 0.5 units
        cameraPositions = new Vector3[4];
        cameraPositions[0] = new Vector3(cameraBuffer, cameraHeight, cameraBuffer);  // Bottom-left corner with buffer
        cameraPositions[1] = new Vector3(roomWidth - cameraBuffer, cameraHeight, cameraBuffer);  // Bottom-right corner with buffer
        cameraPositions[2] = new Vector3(cameraBuffer, cameraHeight, roomLength - cameraBuffer);  // Top-left corner with buffer
        cameraPositions[3] = new Vector3(roomWidth - cameraBuffer, cameraHeight, roomLength - cameraBuffer);  // Top-right corner with buffer

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

        // Look at the center of the room at the same height as the camera
        Vector3 lookAtTarget = new Vector3(roomWidth / 2, cameraPosition.y, roomLength / 2);

        // Apply random rotation between -45 and 45 degrees
        Quaternion rotation = Quaternion.LookRotation(lookAtTarget - cameraPosition);
        rotation = Quaternion.Euler(rotation.eulerAngles.x, rotation.eulerAngles.y + Random.Range(-45f, 45f), rotation.eulerAngles.z);

        // Move the camera and apply rotation
        mainCamera.transform.position = cameraPosition;
        mainCamera.transform.rotation = rotation;
    }
}
