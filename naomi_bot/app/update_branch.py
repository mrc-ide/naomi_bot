from gidgethub import InvalidField

from .utils import text_from_base64
from .utils import text_to_base64
from .version import remove_branch_pin
from .version import update_docker_build
from .version import update_naomi_version


async def update_branch(gh, repo_url, naomi_version, naomi_branch,
                        hintr_new_branch):
    print("Creating new hintr branch " + hintr_new_branch +
          " for update naomi version " + naomi_version +
          " on branch " + naomi_branch)
    # Create new branch
    # Get master reference
    master = await gh.getitem(repo_url + "/git/ref/heads/master")

    # Create new reference pinned to master
    try:
        await gh.post(repo_url + "/git/refs", data={
            "ref": "refs/heads/" + hintr_new_branch,
            "sha": master["object"]["sha"]
        })
        print("Created " + hintr_new_branch + " at master ref " +
              master["object"]["sha"])
    except InvalidField as e:
        message = e.args[0]
        if message == "Reference already exists":
            await gh.patch(repo_url + "/git/refs/heads/" + hintr_new_branch,
                           data={
                               "sha": master["object"]["sha"]
                           })
            print(
                "Updated " + hintr_new_branch + " to master ref " +
                master["object"]["sha"])
            pass
        else:
            print("Can't set " + hintr_new_branch + " to master ref " +
                  master["object"]["sha"] + ", branch is ahead of master")
            raise

    # Make code change
    # Update DESCRIPTION - naomi version
    description = await gh.getitem(repo_url + "/contents/DESCRIPTION")
    desc_text = text_from_base64(description["content"])
    new_desc = update_naomi_version(desc_text, naomi_version)
    await gh.put(repo_url + "/contents/DESCRIPTION", data={
        "message": "Update naomi version in DESCRIPTION",
        "content": text_to_base64(new_desc),
        "sha": description["sha"],
        "branch": hintr_new_branch
    })

    # Update docker build
    docker = await gh.getitem(repo_url + "/contents/docker/build")
    docker_text = text_from_base64(docker["content"])
    new_docker = update_docker_build(docker_text, naomi_branch)
    await gh.put(repo_url + "/contents/docker/build", data={
        "message": "Update naomi version in docker build",
        "content": text_to_base64(new_docker),
        "sha": docker["sha"],
        "branch": hintr_new_branch
    })


async def remove_pin(gh, repo_url, hintr_branch):
    docker = await gh.getitem(repo_url +
                              "/contents/docker/build?ref=refs/heads/" +
                              hintr_branch)
    docker_text = text_from_base64(docker["content"])
    new_docker = remove_branch_pin(docker_text)
    await gh.put(repo_url + "/contents/docker/build", data={
        "message": "Remove branch pin",
        "content": text_to_base64(new_docker),
        "sha": docker["sha"],
        "branch": hintr_branch
    })
