using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class cameramovement : MonoBehaviour
{

    private Transform player_t;

    // Start is called before the first frame update
    void Start()
    {
        player_t = GameObject.FindGameObjectWithTag("Player").transform;
    }

    // Update is called once per frame
    void LateUpdate()
    {
        // store current camera position in tempx
        Vector3 temp = transform.position;

        // set cameras's position (x) equal to player's position (x)
        temp.x = player_t.position.x;
        // set cameras's position (y) equal to player's position (y)
        temp.y = player_t.position.y;

        // set camera's tempx position to camera's current position
        transform.position = temp;
    }
}
