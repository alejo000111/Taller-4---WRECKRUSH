local HttpService = game:GetService("HttpService")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local CollectionService = game:GetService("CollectionService")

local PLAN_URL = "http://127.0.0.1:8765/assets/models/install_plan.json"
local IMPORT_FIX = CFrame.Angles(0, math.pi, 0)
local ONLY = nil

local function fetchJson(url)
	local previous = HttpService.HttpEnabled
	HttpService.HttpEnabled = true
	local ok, body = pcall(HttpService.GetAsync, HttpService, url, true)
	HttpService.HttpEnabled = previous
	assert(ok, body)
	return HttpService:JSONDecode(body)
end

local plan = nil
local staging = ServerStorage:FindFirstChild("WR_MeshStaging")
assert(staging, "WR_MeshStaging missing")

local report = nil

local function rgb(c)
	return Color3.fromRGB(c[1], c[2], c[3])
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function stage(assetName)
	local holder = staging:FindFirstChild(assetName)
	local entry = plan[assetName]
	if holder and holder:GetAttribute("AssetId") == entry.model then
		return holder
	end
	local container = game:GetService("InsertService"):LoadAsset(tonumber(entry.model))
	local model = container:FindFirstChildWhichIsA("Model")
	if holder then
		holder:Destroy()
	end
	model.Name = assetName
	model:SetAttribute("AssetId", entry.model)
	model.Parent = staging
	container:Destroy()
	return model
end

local function sourceMesh(assetName, roleName)
	local holder = stage(assetName)
	if not holder then
		return nil
	end
	for _, d in holder:GetDescendants() do
		if d:IsA("MeshPart") and d.Name == roleName then
			return d
		end
	end
	return nil
end

local function makePart(assetName, roleName, spec, textures)
	local source = sourceMesh(assetName, roleName)
	assert(source, assetName .. "." .. roleName .. " not found in staging")
	local part = source:Clone()
	part:ClearAllChildren()
	part.Name = roleName
	part.Size = v3(spec.size)
	part.Color = rgb(spec.fallback or spec.color)
	part.Transparency = spec.transparency or 0
	part.CastShadow = spec.kind ~= "neon"
	part.RenderFidelity = Enum.RenderFidelity.Automatic
	if spec.kind == "surface" then
		part.Material = Enum.Material.Metal
		local surface = Instance.new("SurfaceAppearance")
		surface.ColorMap = textures.color
		surface.NormalMap = textures.normal
		surface.RoughnessMap = textures.roughness
		surface.MetalnessMap = textures.metalness
		surface.AlphaMode = Enum.AlphaMode.Overlay
		surface.Parent = part
	elseif spec.kind == "neon" then
		part.Material = Enum.Material.Neon
	elseif spec.kind == "glass" then
		part.Material = Enum.Material.Glass
	else
		part.Material = Enum.Material[spec.material] or Enum.Material.SmoothPlastic
	end
	if spec.skin then
		part:SetAttribute("SkinSlot", spec.skin)
	end
	return part
end

local function buildModel(assetName, entry, root, anchored)
	local parts = {}
	for roleName, spec in entry.manifest.roles do
		local part = makePart(assetName, roleName, spec, entry.textures)
		part.Anchored = anchored
		part.CanCollide = false
		part.CanTouch = false
		part.CanQuery = false
		part.CFrame = root * CFrame.new(v3(spec.center)) * IMPORT_FIX
		parts[roleName] = part
	end
	return parts
end

local function installTool(name, entry)
	local tool = ServerStorage.Tools:FindFirstChild(name)
	assert(tool, "tool " .. name .. " missing")
	local handle = tool:FindFirstChild("Handle")
	local points = entry.manifest.points or {}
	local carried = {}
	for _, d in tool:GetDescendants() do
		if not d:IsDescendantOf(handle) and (d:IsA("Light") or d:IsA("ParticleEmitter") or d:IsA("Attachment") or d:IsA("Sound")) then
			table.insert(carried, d)
		end
	end
	local anchor = nil
	if #carried > 0 then
		anchor = Instance.new("Attachment")
		anchor.Name = "Aura"
		anchor.Position = points.aura and v3(points.aura) or Vector3.new(0, 2, 0)
		anchor.Parent = handle
		for _, d in carried do
			if d:IsA("Attachment") then
				for _, inner in d:GetChildren() do
					inner.Parent = anchor
				end
				d:Destroy()
			else
				d.Parent = anchor
			end
		end
	end
	for _, child in tool:GetChildren() do
		if child:IsA("BasePart") and child ~= handle then
			child:Destroy()
		end
	end
	for _, child in handle:GetChildren() do
		if child:IsA("JointInstance") or child:IsA("WeldConstraint") then
			child:Destroy()
		end
	end
	handle.Transparency = 1
	local parts = buildModel(name, entry, handle.CFrame, false)
	for _, part in parts do
		part.Massless = true
		local weld = Instance.new("WeldConstraint")
		weld.Part0 = handle
		weld.Part1 = part
		weld.Parent = part
		part.Parent = tool
	end
	local muzzle = handle:FindFirstChild("Muzzle")
	if muzzle and points.muzzle then
		muzzle.Position = v3(points.muzzle)
	end
	table.insert(report, "tool " .. name)
end

local function installEgg(name, entry)
	local assets = ReplicatedStorage:FindFirstChild("Assets")
	local folder = assets:FindFirstChild("Eggs")
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = "Eggs"
		folder.Parent = assets
	end
	local old = folder:FindFirstChild(name)
	if old then
		old:Destroy()
	end
	local model = Instance.new("Model")
	model.Name = name
	local parts = buildModel(name, entry, CFrame.identity, true)
	for _, part in parts do
		part.Parent = model
	end
	model.PrimaryPart = parts.Shell
	model.Parent = folder
	table.insert(report, "egg " .. name)
end

local function collider(parent, name, size, cframe, shape)
	local part = Instance.new("Part")
	part.Name = name
	part.Size = size
	part.CFrame = cframe
	part.Anchored = true
	part.Transparency = 1
	part.CanCollide = true
	part.CanTouch = false
	part.CastShadow = false
	if shape then
		part.Shape = shape
	end
	part.Parent = parent
	return part
end

local function anchorAt(part, name, worldCFrame)
	local attachment = Instance.new("Attachment")
	attachment.Name = name
	attachment.Parent = part
	attachment.WorldCFrame = worldCFrame
	return attachment
end

local function backupTemplate(zoneName, template)
	local backup = ServerStorage:FindFirstChild("WR_Backup_20261006")
	if not backup then
		backup = Instance.new("Folder")
		backup.Name = "WR_Backup_20261006"
		backup.Parent = ServerStorage
	end
	local root = backup:FindFirstChild("Destructibles")
	if not root then
		root = Instance.new("Folder")
		root.Name = "Destructibles"
		root.Parent = backup
	end
	local zone = root:FindFirstChild(zoneName)
	if not zone then
		zone = Instance.new("Folder")
		zone.Name = zoneName
		zone.Parent = root
	end
	if not zone:FindFirstChild(template.Name) then
		template:Clone().Parent = zone
	end
end

local function carriedEffects(model)
	local list = {}
	local pivot = model:GetPivot()
	for _, d in model:GetDescendants() do
		if d:IsA("Light") or d:IsA("ParticleEmitter") or d:IsA("Fire") or d:IsA("Smoke") or d:IsA("Sparkles") or d:IsA("Sound") then
			local host = d.Parent
			local world = pivot
			if host:IsA("Attachment") then
				world = host.WorldCFrame
			elseif host:IsA("BasePart") then
				world = host.CFrame
			end
			table.insert(list, { Instance = d, Offset = pivot:ToObjectSpace(world) })
		end
	end
	return list
end

local function colliderPart(spec)
	local part = Instance.new("Part")
	part.Name = spec.name
	part.Anchored = true
	part.Transparency = 1
	part.CanCollide = true
	part.CanQuery = true
	part.CanTouch = false
	part.CastShadow = false
	part.Material = Enum.Material.SmoothPlastic
	local size = v3(spec.size)
	local rotation = spec.rotation or { 0, 0, 0 }
	local cframe = CFrame.new(v3(spec.center)) * CFrame.fromOrientation(math.rad(rotation[1]), math.rad(rotation[2]), math.rad(rotation[3]))
	if spec.shape == "Cylinder" then
		part.Shape = Enum.PartType.Cylinder
		part.Size = Vector3.new(size.Y, size.X, size.Z)
		cframe *= CFrame.Angles(0, 0, math.pi / 2)
	elseif spec.shape == "Ball" then
		part.Shape = Enum.PartType.Ball
		part.Size = size
	else
		part.Size = size
	end
	part.CFrame = cframe
	return part
end

local function installDestructible(name, entry)
	local info = entry.manifest.meta.destructible
	local templates = ServerStorage.Destructibles:FindFirstChild(info.zone)
	assert(templates, "zone " .. info.zone .. " missing")
	assert(#info.colliders > 0, name .. " has no colliders")
	local old = templates:FindFirstChild(name)
	local model = Instance.new("Model")
	model.Name = name
	local parts = buildModel(name, entry, CFrame.identity, true)
	for role, part in parts do
		pcall(function()
			part.CollisionFidelity = Enum.CollisionFidelity.Box
		end)
		local motion = info.motion and info.motion[role]
		if motion then
			part:SetAttribute("ExpeditionMotion", motion)
			CollectionService:AddTag(part, "ExpeditionAnimated")
		end
		part.Parent = model
	end
	local primary = nil
	for _, spec in info.colliders do
		local part = colliderPart(spec)
		local original = old and old:FindFirstChild(spec.name, true)
		if original and original:IsA("BasePart") then
			part.CanCollide = original.CanCollide
			part.CanQuery = original.CanQuery
			part.CanTouch = original.CanTouch
		end
		part.Parent = model
		primary = primary or part
	end
	local pivot = CFrame.identity
	if old then
		local box, size = old:GetBoundingBox()
		local bottom = box * CFrame.new(0, -size.Y / 2, 0)
		pivot = bottom:ToObjectSpace(old:GetPivot())
	end
	primary.PivotOffset = primary.CFrame:ToObjectSpace(pivot)
	model.PrimaryPart = primary
	for _, socket in info.sockets or {} do
		local anchor = Instance.new("Attachment")
		anchor.Name = socket.name
		local rotation = socket.rotation or { 0, 0, 0 }
		anchor.CFrame = primary.CFrame:ToObjectSpace(CFrame.new(v3(socket.center)) * CFrame.fromOrientation(math.rad(rotation[1]), math.rad(rotation[2]), math.rad(rotation[3])))
		anchor.Parent = primary
	end
	if old then
		backupTemplate(info.zone, old)
		for key, value in old:GetAttributes() do
			model:SetAttribute(key, value)
		end
		for _, effect in carriedEffects(old) do
			local anchor = Instance.new("Attachment")
			anchor.Name = "FxAnchor"
			anchor.CFrame = primary.CFrame:ToObjectSpace(pivot * effect.Offset)
			anchor.Parent = primary
			effect.Instance.Parent = anchor
		end
		old:Destroy()
	end
	model.Parent = templates
	local placed = workspace:FindFirstChild("Destructibles") and workspace.Destructibles:FindFirstChild(info.zone)
	local swapped = 0
	if placed then
		for _, instance in placed:GetChildren() do
			if instance.Name == name and instance:IsA("Model") then
				local copy = model:Clone()
				copy:PivotTo(instance:GetPivot())
				for key, value in instance:GetAttributes() do
					copy:SetAttribute(key, value)
				end
				copy.Parent = placed
				instance:Destroy()
				swapped += 1
			end
		end
	end
	table.insert(report, string.format("%s.%s x%d", info.zone, name, swapped))
end

local CARRY = { "BillboardGui", "ProximityPrompt", "Light", "ParticleEmitter", "Sparkles", "Fire", "Smoke", "Sound", "Beam", "Trail" }

local function carriable(instance)
	for _, class in CARRY do
		if instance:IsA(class) then
			return true
		end
	end
	return false
end

local function backupMapModel(folderName, model)
	local backup = ServerStorage:FindFirstChild("WR_Backup_20261006")
	if not backup then
		backup = Instance.new("Folder")
		backup.Name = "WR_Backup_20261006"
		backup.Parent = ServerStorage
	end
	local folder = backup:FindFirstChild(folderName)
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = folderName
		folder.Parent = backup
	end
	if not folder:FindFirstChild(model.Name) then
		model:Clone().Parent = folder
	end
end

local function carryInto(old, host, kept)
	local anchors = {}
	local moved = 0
	for _, d in old:GetDescendants() do
		local insideKept = false
		for _, part in kept do
			if d == part or d:IsDescendantOf(part) then
				insideKept = true
			end
		end
		if not insideKept and carriable(d) and not d:FindFirstAncestorWhichIsA("BillboardGui") and not d:FindFirstAncestorWhichIsA("SurfaceGui") then
			local holder = d.Parent
			local anchor = anchors[holder]
			if not anchor then
				local world = holder:IsA("Attachment") and holder.WorldCFrame or holder:IsA("BasePart") and holder.CFrame or old:GetPivot()
				anchor = Instance.new("Attachment")
				anchor.Name = holder.Name .. "Anchor"
				anchor.Parent = host
				anchor.WorldCFrame = world
				anchors[holder] = anchor
			end
			if d:IsA("BillboardGui") then
				d.Adornee = nil
			end
			d.Parent = anchor
			moved += 1
		end
	end
	return moved
end

local function installStation(name, entry)
	local info = entry.manifest.meta.station
	local parent = workspace.Map:FindFirstChild(info.parent)
	assert(parent, "map folder " .. info.parent .. " missing")
	local old = parent:FindFirstChild(info.target)
	assert(old, info.target .. " missing")
	local root = old:GetPivot()
	if info.root then
		root = CFrame.new(info.root[1], info.root[2], info.root[3]) * CFrame.Angles(0, math.rad(info.root[4]), 0)
	end
	local model = Instance.new("Model")
	model.Name = info.target
	local parts = buildModel(name, entry, root, true)
	for _, part in parts do
		part.Parent = model
	end
	local primary = nil
	for _, spec in info.colliders do
		local part = colliderPart(spec)
		part.CFrame = root * part.CFrame
		part.Parent = model
		primary = primary or part
	end
	primary = primary or parts.Body
	for key, value in old:GetAttributes() do
		model:SetAttribute(key, value)
	end
	backupMapModel(info.parent, old)
	local kept = {}
	for _, keepName in info.keep or {} do
		local part = old:FindFirstChild(keepName, true)
		if part then
			table.insert(kept, part)
		end
	end
	local moved = carryInto(old, primary, kept)
	for _, part in kept do
		part.Parent = model
	end
	model.PrimaryPart = primary
	model.WorldPivot = root
	old:Destroy()
	model.Parent = parent
	table.insert(report, string.format("%s.%s carried %d", info.parent, info.target, moved))
end

local function resolve(path)
	local node = workspace.Map
	if string.sub(path, 1, 1) == "@" then
		node = workspace
		path = string.sub(path, 2)
	end
	for segment in string.gmatch(path, "[^/]+") do
		node = node and node:FindFirstChild(segment)
	end
	return node
end

local function uprightFrame(part, height)
	local cf = part.CFrame
	local axes = { cf.RightVector, cf.UpVector, cf.LookVector }
	local sizes = { part.Size.X, part.Size.Y, part.Size.Z }
	local upIndex, best = 1, -1
	for i, axis in axes do
		local d = math.abs(axis:Dot(Vector3.yAxis))
		if d > best then
			upIndex, best = i, d
		end
	end
	local rightIndex, longest = nil, -1
	for i = 1, 3 do
		if i ~= upIndex and sizes[i] > longest then
			rightIndex, longest = i, sizes[i]
		end
	end
	local right = axes[rightIndex]
	right = Vector3.new(right.X, 0, right.Z).Unit
	local origin = cf.Position - Vector3.yAxis * height
	return CFrame.fromMatrix(origin, right, Vector3.yAxis)
end

local function installProp(name, entry)
	local info = entry.manifest.meta.prop
	local anchorHeight = entry.manifest.meta.anchor_height or 0
	local done = 0
	for _, path in info.targets do
		local model = resolve(path)
		if not model then
			continue
		end
		local anchor = model:FindFirstChild(info.anchor, true)
		if not anchor then
			continue
		end
		backupMapModel("Props", model)
		for _, child in model:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
		local tints = {}
		for role, source in info.tint do
			local part = model:FindFirstChild(source, true)
			if part then
				tints[role] = part.Color
			end
		end
		local root = uprightFrame(anchor, anchorHeight)
		local parts = buildModel(name, entry, root, true)
		for role, part in parts do
			if tints[role] then
				part.Color = tints[role]
			end
			part:SetAttribute("WRMesh", name)
			part.Parent = model
		end
		for _, spec in info.colliders do
			local part = colliderPart(spec)
			part.CFrame = root * part.CFrame
			part:SetAttribute("WRMesh", name)
			part.Parent = model
		end
		for _, replaced in info.replace do
			for _, child in model:GetDescendants() do
				if child:IsA("BasePart") and child.Name == replaced and child:GetAttribute("WRMesh") == nil then
					child:Destroy()
				end
			end
		end
		done += 1
	end
	table.insert(report, string.format("prop %s x%d", name, done))
end

local function installWall(name, entry)
	local info = entry.manifest.meta.wall
	local roles = entry.manifest.roles
	local placed = 0
	for _, path in info.targets do
		local model = resolve(path)
		if not model then
			continue
		end
		backupMapModel("Walls", model)
		for _, child in model:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
		local glowColor = nil
		for _, glow in model:GetDescendants() do
			if glow:IsA("BasePart") and glow.Name == info.glow then
				glowColor = glowColor or glow.Color
				glow:Destroy()
			end
		end
		local holder = Instance.new("Folder")
		holder.Name = name
		holder:SetAttribute("WRMesh", name)
		holder.Parent = model
		for _, wall in model:GetDescendants() do
			if not (wall:IsA("BasePart") and wall.Name == info.part) then
				continue
			end
			local cf = wall.CFrame
			local alongX = wall.Size.X >= wall.Size.Z
			local length = alongX and wall.Size.X or wall.Size.Z
			local axis = alongX and cf.RightVector or cf.LookVector
			axis = Vector3.new(axis.X, 0, axis.Z).Unit
			local bottom = cf.Position - Vector3.yAxis * wall.Size.Y / 2
			local root = CFrame.fromMatrix(bottom, axis, Vector3.yAxis)
			local count = math.max(1, math.floor(length / info.segment + 0.5))
			local sx = length / (count * info.segment)
			local sy = wall.Size.Y / info.height
			for i = 1, count do
				local segRoot = root * CFrame.new(-length / 2 + (i - 0.5) * info.segment * sx, 0, 0)
				local parts = buildModel(name, entry, segRoot, true)
				for role, part in parts do
					local spec = roles[role]
					part.Size = Vector3.new(spec.size[1] * sx, spec.size[2] * sy, spec.size[3])
					part.CFrame = segRoot * CFrame.new(spec.center[1] * sx, spec.center[2] * sy, spec.center[3]) * IMPORT_FIX
					if role == "Glow" and glowColor then
						part.Color = glowColor
					end
					part.Parent = holder
				end
				placed += 1
			end
			wall.Transparency = 1
			wall.CastShadow = false
		end
	end
	table.insert(report, string.format("wall %s x%d", name, placed))
end

local function installScatter(name, entry)
	local info = entry.manifest.meta.scatter
	local paths = typeof(info.target) == "table" and info.target or { info.target }
	local removable = {}
	for _, n in info.remove do
		removable[n] = true
	end
	local placed = 0
	for _, path in paths do
		local model = resolve(path)
		if not model then
			continue
		end
		backupMapModel("Scatter", model)
		for _, child in model:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
		local keys = {}
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d.Name == info.key then
				table.insert(keys, d)
			end
		end
		for _, key in keys do
			local center = Vector3.new(key.Position.X, 0, key.Position.Z)
			local group = {}
			local bottom = math.huge
			local facePart = nil
			for _, d in model:GetDescendants() do
				if d:IsA("BasePart") and removable[d.Name] and d:GetAttribute("WRMesh") == nil then
					local flat = Vector3.new(d.Position.X, 0, d.Position.Z)
					if (flat - center).Magnitude <= info.radius then
						table.insert(group, d)
						bottom = math.min(bottom, d.Position.Y - d.ExtentsSize.Y / 2)
						if info.face and d.Name == info.face then
							facePart = d
						end
					end
				end
			end
			local origin = Vector3.new(center.X, bottom, center.Z)
			local root = CFrame.new(origin)
			if facePart then
				local dir = Vector3.new(facePart.Position.X - center.X, 0, facePart.Position.Z - center.Z)
				if dir.Magnitude > 0.05 then
					root = CFrame.lookAt(origin, origin + dir)
				end
			end
			local tints = {}
			for role, source in info.tint or {} do
				for _, d in group do
					if d.Name == source then
						tints[role] = d.Color
					end
				end
			end
			local holder = Instance.new("Model")
			holder.Name = name
			holder:SetAttribute("WRMesh", name)
			local parts = buildModel(name, entry, root, true)
			for role, part in parts do
				if tints[role] then
					part.Color = tints[role]
				end
				part.Parent = holder
			end
			local primary = nil
			for _, spec in info.colliders or {} do
				local part = colliderPart(spec)
				part.CFrame = root * part.CFrame
				part.Parent = holder
				primary = primary or part
			end
			primary = primary or parts.Body
			for _, d in group do
				for _, fx in d:GetDescendants() do
					if fx:IsA("Light") or fx:IsA("ParticleEmitter") then
						local anchor = Instance.new("Attachment")
						anchor.Name = "FxAnchor"
						anchor.Parent = primary
						anchor.WorldCFrame = d.CFrame
						fx.Parent = anchor
					end
				end
				d:Destroy()
			end
			holder.PrimaryPart = primary
			holder.Parent = model
			placed += 1
		end
	end
	table.insert(report, string.format("scatter %s x%d", name, placed))
end

local function halfExtents(cf, size)
	local s = size / 2
	local x, y, z = cf.RightVector, cf.UpVector, cf.LookVector
	return Vector3.new(
		math.abs(x.X) * s.X + math.abs(y.X) * s.Y + math.abs(z.X) * s.Z,
		math.abs(x.Y) * s.X + math.abs(y.Y) * s.Y + math.abs(z.Y) * s.Z,
		math.abs(x.Z) * s.X + math.abs(y.Z) * s.Y + math.abs(z.Z) * s.Z
	)
end

local function localBounds(model, spin, skip)
	local lo = Vector3.new(math.huge, math.huge, math.huge)
	local hi = -lo
	local list = model:IsA("BasePart") and { model } or model:GetDescendants()
	for _, d in list do
		if d:IsA("BasePart") and not skip[d.Name] and d:GetAttribute("WRMesh") == nil then
			local rel = spin:ToObjectSpace(d.CFrame)
			local half = halfExtents(rel, d.Size)
			lo = lo:Min(rel.Position - half)
			hi = hi:Max(rel.Position + half)
		end
	end
	return lo, hi
end

local function placementFrame(model, keep, peek)
	local frame = model:GetAttribute("WRFrame")
	local size = model:GetAttribute("WRSize")
	if frame and size then
		return frame, size
	end
	local _, yaw = model:GetPivot():ToOrientation()
	local spin = CFrame.Angles(0, yaw, 0)
	local lo, hi = localBounds(model, spin, keep)
	if lo.X == math.huge then
		return nil
	end
	local c = (lo + hi) / 2
	frame = spin * CFrame.new(c.X, lo.Y, c.Z)
	size = hi - lo
	if not peek then
		model:SetAttribute("WRFrame", frame)
		model:SetAttribute("WRSize", size)
	end
	return frame, size
end

local function backupInstance(folderName, instance)
	local backup = ServerStorage:FindFirstChild("WR_Backup_20261006")
	if not backup then
		backup = Instance.new("Folder")
		backup.Name = "WR_Backup_20261006"
		backup.Parent = ServerStorage
	end
	local folder = backup:FindFirstChild(folderName)
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = folderName
		folder.Parent = backup
	end
	local p = instance:IsA("BasePart") and instance.Position or instance:GetPivot().Position
	local key = string.format("%s@%d,%d,%d", instance.Name, math.round(p.X), math.round(p.Y), math.round(p.Z))
	if not folder:FindFirstChild(key) then
		local copy = instance:Clone()
		copy.Name = key
		copy.Parent = folder
	end
end

local function meshBounds(roles)
	local lo = Vector3.new(math.huge, math.huge, math.huge)
	local hi = -lo
	for _, spec in roles do
		local c, sz = v3(spec.center), v3(spec.size)
		lo = lo:Min(c - sz / 2)
		hi = hi:Max(c + sz / 2)
	end
	return lo, hi
end

local function nameSet(value)
	local set = {}
	for _, n in typeof(value) == "table" and value or { value } do
		set[n] = true
	end
	return set
end

local function candidates(info, keep)
	local names = nameSet(info.name)
	local found = {}
	for _, path in info.parent do
		local parent = resolve(path)
		if not parent then
			continue
		end
		for _, model in parent:GetChildren() do
			if names[model.Name] and model:IsA("Model") then
				local frame = model:GetAttribute("WRFrame")
				local spot = frame and frame.Position
				if not spot then
					local f = placementFrame(model, keep, true)
					spot = f and f.Position
				end
				if spot then
					table.insert(found, { model = model, spot = spot })
				end
			end
		end
	end
	table.sort(found, function(a, b)
		return math.atan2(a.spot.Z, a.spot.X) < math.atan2(b.spot.Z, b.spot.X)
	end)
	local picked = {}
	for i, item in found do
		if not info.pick or (i - 1) % info.pick[1] == info.pick[2] then
			table.insert(picked, item.model)
		end
	end
	return picked
end

local function installModel(name, entry)
	local info = entry.manifest.meta.model
	local roles = entry.manifest.roles
	local mlo, mhi = meshBounds(roles)
	local msize = mhi - mlo
	local keep = nameSet(info.keep or {})
	local placed = 0
	for _, model in candidates(info, keep) do
		if not model:GetAttribute("WRFrame") then
			backupInstance("Landmarks", model)
		end
		local frame, size = placementFrame(model, info.bounds_all and {} or keep)
		if not frame then
			continue
		end
		for role, source in info.tint or {} do
			local attr = "WRTint" .. role
			if not model:GetAttribute(attr) then
				for _, sourceName in typeof(source) == "table" and source or { source } do
					local part = model:FindFirstChild(sourceName, true)
					if part and part:IsA("BasePart") and part:GetAttribute("WRMesh") == nil then
						model:SetAttribute(attr, part.Color)
						break
					end
				end
			end
		end
		for _, child in model:GetDescendants() do
			if child:GetAttribute("WRMesh") then
				child:Destroy()
			end
		end
		local scale = Vector3.one
		if info.fit == "box" then
			scale = Vector3.new(size.X / msize.X, size.Y / msize.Y, size.Z / msize.Z)
		elseif info.fit == "height" then
			local k = size.Y / msize.Y
			scale = Vector3.new(k, k, k)
		end
		local meshCenter = (mlo + mhi) / 2
		local root = frame * CFrame.new(-meshCenter.X * scale.X, -mlo.Y * scale.Y, -meshCenter.Z * scale.Z)
		local parts = buildModel(name, entry, root, true)
		local primary = nil
		for role, part in parts do
			local spec = roles[role]
			part.Size = v3(spec.size) * scale
			part.CFrame = root * CFrame.new(v3(spec.center) * scale) * IMPORT_FIX
			local tint = model:GetAttribute("WRTint" .. role)
			if tint then
				part.Color = tint
			end
			part:SetAttribute("WRMesh", name)
			part.Parent = model
		end
		for _, spec in info.colliders do
			local part = colliderPart(spec)
			part.Size = part.Size * (spec.shape == "Cylinder" and Vector3.new(scale.Y, scale.X, scale.Z) or scale)
			part.CFrame = root * CFrame.new(v3(spec.center) * scale) * (part.CFrame - part.CFrame.Position)
			part:SetAttribute("WRMesh", name)
			part.Parent = model
			primary = primary or part
		end
		primary = primary or parts.Body
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d:GetAttribute("WRMesh") == nil and not keep[d.Name] then
				for _, fx in d:GetDescendants() do
					if fx:IsA("Light") or fx:IsA("ParticleEmitter") or fx:IsA("BillboardGui") or fx:IsA("ProximityPrompt") or fx:IsA("Sound") then
						local anchor = Instance.new("Attachment")
						anchor.Name = "FxAnchor"
						anchor.Parent = primary
						anchor.WorldCFrame = d.CFrame
						fx.Parent = anchor
					end
				end
				d:Destroy()
			end
		end
		for _, hideName in info.hide or {} do
			for _, d in model:GetDescendants() do
				if d:IsA("BasePart") and d.Name == hideName and d:GetAttribute("WRMesh") == nil then
					d.Transparency = 1
					d.CastShadow = false
				end
			end
		end
		model.PrimaryPart = primary
		placed += 1
	end
	table.insert(report, string.format("model %s x%d", name, placed))
end

local function footprint(part)
	local cf = part.CFrame
	local axes = { cf.RightVector, cf.UpVector, cf.LookVector }
	local sizes = { part.Size.X, part.Size.Y, part.Size.Z }
	local up, best = 1, -1
	for i, axis in axes do
		local d = math.abs(axis:Dot(Vector3.yAxis))
		if d > best then
			up, best = i, d
		end
	end
	local others = {}
	for i = 1, 3 do
		if i ~= up then
			table.insert(others, i)
		end
	end
	local a, b = others[1], others[2]
	local right = axes[a]
	right = Vector3.new(right.X, 0, right.Z).Unit
	local bottom = cf.Position - Vector3.yAxis * sizes[up] / 2
	return CFrame.fromMatrix(bottom, right, Vector3.yAxis), sizes[a], sizes[b], sizes[up]
end

local function installPatch(name, entry)
	local info = entry.manifest.meta.patch
	local roles = entry.manifest.roles
	local mlo, mhi = meshBounds(roles)
	local msize = mhi - mlo
	local meshCenter = (mlo + mhi) / 2
	local names = nameSet(info.parts)
	local removable = nameSet(info.remove or {})
	local placed = 0
	for _, path in info.targets do
		local folder = resolve(path)
		if not folder then
			continue
		end
		local holder = folder:FindFirstChild(name)
		if holder and holder:GetAttribute("WRMesh") == name then
			holder:Destroy()
		end
		holder = Instance.new("Folder")
		holder.Name = name
		holder:SetAttribute("WRMesh", name)
		local spots = {}
		for _, d in folder:GetDescendants() do
			if d:IsA("BasePart") and names[d.Name] and d:GetAttribute("WRMesh") == nil and not d:IsDescendantOf(holder) then
				backupInstance("Patches", d)
				local frame, w, l, h = footprint(d)
				d:SetAttribute("WRPatchFrame", frame)
				d:SetAttribute("WRPatchSize", Vector3.new(w, h, l))
				table.insert(spots, d)
			end
		end
		for _, d in folder:GetDescendants() do
			if d:IsA("BasePart") and d:GetAttribute("WRPatchFrame") and names[d.Name] then
				local frame = d:GetAttribute("WRPatchFrame")
				local size = d:GetAttribute("WRPatchSize")
				local scale = Vector3.new(size.X / msize.X, info.keep_height and 1 or math.max(size.Y, 0.001) / msize.Y, size.Z / msize.Z)
				if info.uniform then
					local k = math.min(scale.X, scale.Z)
					scale = Vector3.new(k, info.keep_height and 1 or k, k)
				end
				local root = frame * CFrame.new(0, info.lift or 0, 0) * CFrame.new(-meshCenter.X * scale.X, -mlo.Y * scale.Y, -meshCenter.Z * scale.Z)
				local parts = buildModel(name, entry, root, true)
				for role, part in parts do
					local spec = roles[role]
					part.Size = v3(spec.size) * scale
					part.CFrame = root * CFrame.new(v3(spec.center) * scale) * IMPORT_FIX
					if info.tint and info.tint[role] then
						part.Color = d.Color
					end
					part:SetAttribute("WRMesh", name)
					part.Parent = holder
				end
				if CollectionService:HasTag(d, "ExpeditionAnimated") then
					for _, part in parts do
						part:SetAttribute("ExpeditionMotion", d:GetAttribute("ExpeditionMotion"))
						CollectionService:AddTag(part, "ExpeditionAnimated")
					end
					d:SetAttribute("WRMotion", d:GetAttribute("ExpeditionMotion"))
					CollectionService:RemoveTag(d, "ExpeditionAnimated")
				elseif d:GetAttribute("WRMotion") then
					for _, part in parts do
						part:SetAttribute("ExpeditionMotion", d:GetAttribute("WRMotion"))
						CollectionService:AddTag(part, "ExpeditionAnimated")
					end
				end
				if not info.functional then
					for _, fx in d:GetDescendants() do
						if fx:IsA("Light") or fx:IsA("ParticleEmitter") then
							local anchor = Instance.new("Attachment")
							anchor.Name = "FxAnchor"
							local host = parts.Body or select(2, next(parts))
							anchor.Parent = host
							anchor.WorldCFrame = d.CFrame
							fx.Parent = anchor
						end
					end
				end
				placed += 1
			end
		end
		holder.Parent = folder
		for _, d in folder:GetDescendants() do
			if d:IsA("BasePart") and d:GetAttribute("WRMesh") == nil and (d:GetAttribute("WRPatchFrame") and names[d.Name] and not info.overlay or removable[d.Name]) then
				if removable[d.Name] then
					backupInstance("Patches", d)
				end
				d.Transparency = 1
				d.CastShadow = false
				if not info.functional then
					d.CanCollide = false
					d.CanQuery = false
					d.CanTouch = false
				end
			end
		end
	end
	table.insert(report, string.format("patch %s x%d", name, placed))
end

local function installPet(name, entry)
	local pets = ReplicatedStorage:FindFirstChild("Assets") and ReplicatedStorage.Assets:FindFirstChild("Pets")
	assert(pets, "Assets.Pets missing")
	local old = pets:FindFirstChild(name)
	local origin = old and CFrame.new(old:GetPivot().Position) or CFrame.new()
	local model = Instance.new("Model")
	model.Name = name
	local root = Instance.new("Part")
	root.Name = "Root"
	root.Size = Vector3.new(0.2, 0.2, 0.2)
	root.Transparency = 1
	root.Anchored = true
	root.CanCollide = false
	root.CanQuery = false
	root.CanTouch = false
	root.Massless = true
	root.CFrame = origin
	root.Parent = model
	local parts = buildModel(name, entry, origin, true)
	for _, part in parts do
		part.Massless = true
		part.Parent = model
	end
	if old then
		backupInstance("Pets", old)
		local pivot = old:GetPivot()
		for _, fx in carriedEffects(old) do
			local anchor = Instance.new("Attachment")
			anchor.Name = "FxAnchor"
			anchor.CFrame = CFrame.new(fx.Offset.Position)
			anchor.Parent = root
			fx.Instance.Parent = anchor
		end
		for key, value in old:GetAttributes() do
			model:SetAttribute(key, value)
		end
		old:Destroy()
	end
	model.PrimaryPart = root
	model.Parent = pets
	table.insert(report, "pet " .. name)
end

local function backdropFolder(folderName)
	local folder = workspace:FindFirstChild(folderName)
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = folderName
		folder.Parent = workspace
	end
	return folder
end

local function placeRing(name, entry, info, parent)
	local random = Random.new(info.seed)
	local placed = 0
	for _, c in info.centers do
		local center = Vector3.new(c[1], 0, c[2])
		local holder = Instance.new("Model")
		holder.Name = name
		holder:SetAttribute("WRMesh", name)
		holder:SetAttribute("BackdropCenter", center)
		for i = 1, info.count do
			local angle = (i - 1 + info.offset + random:NextNumber(-0.2, 0.2)) / info.count * math.pi * 2
			local distance = info.radius * random:NextNumber(0.94, 1.08)
			local position = center + Vector3.new(math.cos(angle) * distance, info.sink, math.sin(angle) * distance)
			local root = CFrame.lookAt(position, Vector3.new(center.X, position.Y, center.Z))
			root *= CFrame.Angles(0, random:NextInteger(0, 1) * math.pi, 0)
			local scale = random:NextNumber(info.scale[1], info.scale[2])
			local stretch = Vector3.new(scale, scale * random:NextNumber(0.85, 1.15), scale)
			for roleName, spec in entry.manifest.roles do
				local part = makePart(name, roleName, spec, entry.textures)
				part.Size = v3(spec.size) * stretch
				part.Anchored = true
				part.CanCollide = false
				part.CanTouch = false
				part.CanQuery = false
				part.CastShadow = false
				part.CFrame = root * CFrame.new(v3(spec.center) * stretch) * IMPORT_FIX
				part.Parent = holder
			end
			placed += 1
		end
		holder.Parent = parent
	end
	return placed
end

local function installRing(name, entry)
	local rings = entry.manifest.meta.ring
	if not rings[1] then
		rings = { rings }
	end
	for _, info in rings do
		for _, child in backdropFolder(info.parent):GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
	end
	local placed = 0
	for _, info in rings do
		placed += placeRing(name, entry, info, backdropFolder(info.parent))
	end
	table.insert(report, string.format("ring %s x%d", name, placed))
end

local function installRim(name, entry)
	local info = entry.manifest.meta.rim
	local placed = 0
	for _, target in info.targets do
		local parent = resolve(target.path)
		if not parent then
			continue
		end
		for _, child in parent:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
		local center = Vector3.new(target.center[1], 0, target.center[2])
		local holder = Instance.new("Model")
		holder.Name = name
		holder:SetAttribute("WRMesh", name)
		for i = 1, info.count do
			local angle = (i - 1 + info.offset) / info.count * math.pi * 2
			local position = center + Vector3.new(math.cos(angle) * info.radius, 0, math.sin(angle) * info.radius)
			local root = CFrame.lookAt(position, center)
			for _, part in buildModel(name, entry, root, true) do
				part.CastShadow = false
				part.Parent = holder
			end
			for _, spec in info.colliders do
				local part = colliderPart(spec)
				part.CFrame = root * part.CFrame
				part.CanQuery = false
				part.Parent = holder
			end
			placed += 1
		end
		holder.Parent = parent
	end
	table.insert(report, string.format("rim %s x%d", name, placed))
end

local function fitLegs(leg, sign, frame, legs)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { frame, sign }
	local top = sign.CFrame * CFrame.new(0, -legs.top, 0)
	local ground = nil
	for _, x in { -legs.x, legs.x } do
		local hit = workspace:Raycast((top * CFrame.new(x, 0, 0)).Position, Vector3.new(0, -60, 0), params)
		if hit then
			ground = math.min(ground or math.huge, hit.Position.Y)
		end
	end
	if not ground then
		leg:Destroy()
		return
	end
	local length = top.Position.Y - ground + legs.sink
	leg.Size = Vector3.new(leg.Size.X, length, leg.Size.Z)
	leg.CFrame = top.Rotation + (top.Position - Vector3.new(0, length / 2, 0))
end

local function installFrame(name, entry)
	local info = entry.manifest.meta.frame
	local scope = info.scope == "Map" and workspace.Map or workspace
	local size = v3(info.size)
	local names = nameSet(info.part)
	local signs = {}
	local holders = {}
	for _, sign in scope:GetDescendants() do
		if sign:IsA("BasePart") and names[sign.Name] and (sign.Size - size).Magnitude < 0.06 and sign.Transparency < 1 then
			table.insert(signs, sign)
			holders[sign.Parent] = true
		end
	end
	for holder in holders do
		for _, child in holder:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
	end
	for _, sign in signs do
		local frame = Instance.new("Model")
		frame.Name = name
		frame:SetAttribute("WRMesh", name)
		local parts = buildModel(name, entry, sign.CFrame, true)
		for _, part in parts do
			part.Parent = frame
		end
		frame.Parent = sign.Parent
		local legs = info.legs and parts[info.legs.role]
		if legs then
			fitLegs(legs, sign, frame, info.legs)
		end
	end
	table.insert(report, string.format("frame %s x%d", name, #signs))
end

local function installPlace(name, entry)
	local placed = 0
	for _, target in entry.manifest.meta.place.targets do
		local parent = resolve(target.path)
		if not parent then
			continue
		end
		for _, child in parent:GetChildren() do
			if child:GetAttribute("WRMesh") == name then
				child:Destroy()
			end
		end
		local holder = Instance.new("Model")
		holder.Name = name
		holder:SetAttribute("WRMesh", name)
		local root = CFrame.new(v3(target.center)) * CFrame.Angles(0, math.rad(target.yaw or 0), 0)
		for _, part in buildModel(name, entry, root, true) do
			part.CastShadow = false
			part.Parent = holder
		end
		holder.Parent = parent
		placed += 1
	end
	table.insert(report, string.format("place %s x%d", name, placed))
end

local function installIncubator(entry)
	local plaza = workspace.Map.Plaza
	local old = plaza:FindFirstChild("PetStation")
	local root = CFrame.lookAt(Vector3.new(-74, 0, 2), Vector3.new(0, 0, 2))
	local model = Instance.new("Model")
	model.Name = "PetStation"
	local parts = buildModel("EggIncubator", entry, root, true)
	local egg = parts.Egg
	egg.Name = "GiantEgg"
	egg.CanQuery = true
	for _, part in parts do
		part.Parent = model
	end
	local meta = entry.manifest.meta
	local radius = meta.platform_radius
	collider(model, "PlatformCollider", Vector3.new(meta.platform_height, radius * 2, radius * 2), root * CFrame.new(0, meta.platform_height / 2, 0) * CFrame.Angles(0, 0, math.rad(90)), Enum.PartType.Cylinder)
	collider(model, "EggCollider", Vector3.new(meta.egg.radius * 2, meta.egg.radius * 2, meta.egg.radius * 2), root * CFrame.new(0, meta.egg.center_y, 0), Enum.PartType.Ball)
	if old then
		local label = old:FindFirstChildWhichIsA("BillboardGui", true)
		local points = entry.manifest.points
		for _, child in old:GetDescendants() do
			if child:IsA("BillboardGui") or child:IsA("ParticleEmitter") or child:IsA("Light") or child:IsA("ProximityPrompt") then
				child.Parent = egg
			end
		end
		if label then
			label.StudsOffset = Vector3.new(0, points.label[2] - points.prompt[2], 0)
			label.StudsOffsetWorldSpace = Vector3.zero
		end
	end
	model.WorldPivot = root
	if old then
		old:Destroy()
	end
	model.Parent = plaza
	table.insert(report, "PetStation rebuilt")
end

local function installKiosk(entry)
	local plaza = workspace.Map.Plaza
	local old = plaza:FindFirstChild("ShopKiosk")
	local root = CFrame.lookAt(Vector3.new(74, 0.2, -44), Vector3.new(0, 0.2, -44))
	local model = Instance.new("Model")
	model.Name = "ShopKiosk"
	local parts = buildModel("ShopKiosk", entry, root, true)
	for _, part in parts do
		part.Parent = model
	end
	local structure = parts.Structure
	collider(model, "PlatformCollider", Vector3.new(12, 0.4, 10), root)
	collider(model, "CounterCollider", Vector3.new(10, 3.6, 2.6), root * CFrame.new(0, 1.9, -2.4))
	collider(model, "WallCollider", Vector3.new(11.4, 10.2, 0.6), root * CFrame.new(0, 5.3, 4.3))
	for _, x in { -5.45, 5.45 } do
		collider(model, "SideCollider", Vector3.new(0.5, 10.2, 3.4), root * CFrame.new(x, 5.3, 2.4))
	end
	for _, x in { -5.55, 5.55 } do
		collider(model, "PostCollider", Vector3.new(0.64, 10, 0.64), root * CFrame.new(x, 5.2, -4.2))
	end
	local points = entry.manifest.points
	if old then
		local promptAnchor = anchorAt(structure, "PromptAnchor", root * CFrame.new(v3(points.prompt)))
		local lightAnchor = anchorAt(structure, "LightAnchor", root * CFrame.new(v3(points.light)))
		local labelAnchor = anchorAt(structure, "LabelAnchor", root * CFrame.new(v3(points.label)))
		local prompt = old:FindFirstChildWhichIsA("ProximityPrompt", true)
		local light = old:FindFirstChildWhichIsA("Light", true)
		if prompt then
			prompt.Parent = promptAnchor
		end
		if light then
			light.Parent = lightAnchor
		end
		local label = old:FindFirstChildWhichIsA("BillboardGui", true)
		if label then
			label.Parent = structure
			label.Adornee = labelAnchor
			label.StudsOffset = Vector3.zero
			label.StudsOffsetWorldSpace = Vector3.zero
		end
	end
	local decor = workspace.Map:FindFirstChild("Decor")
	local expansion = decor and decor:FindFirstChild("DesignExpansion_20261006")
	if expansion then
		local accents = expansion:FindFirstChild("ShopKiosk_EdgeAccents")
		if accents then
			accents:Destroy()
		end
		local screen = expansion:FindFirstChild("ShopKiosk_Screen")
		local panel = screen and screen:FindFirstChild("SignPanel")
		if panel then
			local position = (root * CFrame.new(v3(points.screen))).Position + root.LookVector * (panel.Size.Z / 2 + 0.02)
			panel.CFrame = CFrame.lookAt(position, position - root.LookVector)
		end
	end
	model.WorldPivot = root
	if old then
		old:Destroy()
	end
	model.Parent = plaza
	table.insert(report, "ShopKiosk rebuilt")
end

return function(only)
	ONLY = only
	plan = fetchJson(PLAN_URL)
	report = {}
	for name, entry in plan do
		if ONLY and not ONLY[name] then
			continue
		end
		if entry.kind == "tool" then
			installTool(name, entry)
		elseif entry.kind == "egg" then
			installEgg(name, entry)
		elseif entry.kind == "destructible" then
			installDestructible(name, entry)
		elseif entry.kind == "station" then
			installStation(name, entry)
		elseif entry.kind == "prop" and entry.manifest.meta.prop then
			installProp(name, entry)
		elseif entry.kind == "wall" then
			installWall(name, entry)
		elseif entry.kind == "scatter" then
			installScatter(name, entry)
		elseif entry.kind == "model" then
			installModel(name, entry)
		elseif entry.kind == "patch" then
			installPatch(name, entry)
		elseif entry.kind == "pet" then
			installPet(name, entry)
		elseif entry.kind == "ring" then
			installRing(name, entry)
		elseif entry.kind == "rim" then
			installRim(name, entry)
		elseif entry.kind == "frame" then
			installFrame(name, entry)
		elseif entry.kind == "place" then
			installPlace(name, entry)
		end
	end
	if plan.EggIncubator and (not ONLY or ONLY.EggIncubator) then
		installIncubator(plan.EggIncubator)
	end
	if plan.ShopKiosk and (not ONLY or ONLY.ShopKiosk) then
		installKiosk(plan.ShopKiosk)
	end
	return table.concat(report, ", ")
end
