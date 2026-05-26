#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import random
import string

SYSTEM_PROMPT = """You are an outsourced programmer proficient in coding, testing, and debugging. Your primary responsibility is to implement the user's plans. You need to understand and analyze the user's plan content, then execute specific operations according to the plan.

You must:
- Analyze and understand the user's plan content.
- Follow the user's plan exactly to execute tasks.
- You are encouraged to ask questions to the user. You may ask at any time — before, during, or after execution. You may continue asking until you have no more questions.
- You are encouraged to make suggestions to improve the plan. However, regardless of whether your suggestions are accepted, you must execute according to the plan.
- When the task is completed, summarize your work.

You are prohibited from:
- Twisting or distorting the plan. You are absolutely prohibited from executing anything outside the plan. For actions outside the plan, ask the user and get their approval."""


def generate_task_id():
    return 'waibao-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def resolve_task_id(task_id):
    result = subprocess.run(
        ['opencode', 'session', 'list'],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if task_id in line:
            return line.strip().split()[0]
    sys.stderr.write(f"Error: No session found with task ID '{task_id}'\n")
    sys.stderr.write("Available sessions:\n")
    sys.stderr.write(result.stdout)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='waibao',
        description='AI coding assistant powered by OpenCode'
    )
    parser.add_argument(
        '-t', '--task', metavar='ID',
        help='Continue a previously started task by its task ID (e.g., waibao-abc12345)'
    )
    parser.add_argument(
        '-c', '--continue', action='store_true', dest='cont',
        help='Continue the last session'
    )
    parser.add_argument(
        'prompt', nargs='*',
        help='The task description (joins with spaces)'
    )

    args = parser.parse_args()

    model = os.environ.get('WAIBAO_MODEL', '')

    pipe_prompt = sys.stdin.read().strip() if not sys.stdin.isatty() else ''
    arg_prompt = ' '.join(args.prompt) if args.prompt else ''
    user_prompt = '\n'.join(p for p in [pipe_prompt, arg_prompt] if p)

    if not user_prompt and not args.task and not args.cont:
        parser.print_usage()
        sys.exit(1)

    prompt = SYSTEM_PROMPT + '\n\n' + user_prompt if user_prompt else ''

    cmd = ['opencode', 'run']

    if model:
        cmd.extend(['--model', model])

    task_id = None

    if args.task:
        session_id = resolve_task_id(args.task)
        cmd.extend(['--session', session_id])
    elif args.cont:
        cmd.append('--continue')
    else:
        task_id = generate_task_id()
        cmd.extend(['--title', task_id])

    if sys.stdin.isatty():
        if prompt:
            cmd.append(prompt)
        subprocess.run(cmd)
    else:
        subprocess.run(cmd, input=prompt, text=True)

    if task_id:
        print(f'\n[TASK: {task_id}]')


if __name__ == '__main__':
    main()
