using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class playerscript : MonoBehaviour
{
    private bool jumpKeyPressed;
    private Rigidbody2D rigidbodyComponent;
    private float horizontalInput;
    private bool touchingGround;
    public Animator animator;

    // Start is called before the first frame update
    void Start()
    {
        rigidbodyComponent = GetComponent<Rigidbody2D>();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W))
        {
            if (touchingGround)
            {   
                jumpKeyPressed = true;
            }
        }

        if (Input.GetKeyDown(KeyCode.S))
        {
            animator.SetBool("Crouching", true);
        }
        if (Input.GetKeyUp(KeyCode.S))
        {
            animator.SetBool("Crouching", false);
        }

        if (Input.GetKeyDown(KeyCode.Mouse0))
        { 
            animator.SetBool("Attacking", true);
        }

        if (Input.GetKeyDown(KeyCode.Mouse1))
        {
            animator.SetBool("Striking", true);
        }

        horizontalInput = Input.GetAxis("Horizontal");
        Vector3 characterscale = transform.localScale;
        if (Input.GetAxis("Horizontal") < 0)
        {
            characterscale.x = -1;
        }
        if (Input.GetAxis("Horizontal") > 0)
        {
            characterscale.x = 1;
        }
        transform.localScale = characterscale;

        animator.SetFloat("Speed", Mathf.Abs(horizontalInput));
    }

    // FixedUpdate called once every physics update
    private void FixedUpdate()
    {
        rigidbodyComponent.velocity = new Vector2(horizontalInput * 4, rigidbodyComponent.velocity.y);

        if (jumpKeyPressed)
        {   
            rigidbodyComponent.AddForce(Vector2.up * 5, ForceMode2D.Impulse);
            jumpKeyPressed = false;
        }
    }

    // testing if the player is touching the ground (or another collider) 
    private void OnCollisionEnter2D(Collision2D col)
    {   
        //Debug.Log("Touching ground");
        touchingGround = true;
        animator.SetBool("Jumping", false);

    }

    private void OnCollisionExit2D(Collision2D col)
    {
        //Debug.Log("Not grounded");
        touchingGround = false;
        animator.SetBool("Jumping", true);
        
    }

    public void SetAttackingFalse()
    {
        animator.SetBool("Attacking", false);
    }

    public void SetStrikingFalse()
    {
        animator.SetBool("Striking", false);
    }
}
