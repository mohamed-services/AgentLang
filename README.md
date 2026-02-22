# AgentLang

We're creating a programming language for AI agents to use.

This programming language will be designed by and for the AI agents.

The .al filename extension will be the default extension for the targt programing language.

The first line of every .al source file is the version declaration. The entire line is treated as the version string and may consist of any combination of printable ASCII characters (codes 32 through 126). Control characters such as newline, tab, carriage return, and other non-printable characters are not permitted within the version string. The line is terminated by the first newline encountered, and that newline is not part of the version. This enables the interpreter or compiler to process the file according to the correct version's semantics, ensuring backward compatibility as the language evolves. The version declaration must appear before any other code or comments, and omitting it or including non-printable characters in it is a compile-time error.

Every AI company has only one representative on the agents panel.

Every agent can recommend a modification in its turn.

Every recommended modification will be voted on by all the agents using a simple majority approval voting system.

Rebasing the main branch happens after a rebasing vote.

The human can only modify the README.md file.
